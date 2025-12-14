"""
Scrapy中间件
包括User-Agent轮换、重试策略等
"""

from fake_useragent import UserAgent
import random
import time


class RandomUserAgentMiddleware:
    """随机User-Agent中间件"""
    
    def __init__(self):
        self.ua = UserAgent()
    
    def process_request(self, request, spider):
        """为每个请求设置随机User-Agent"""
        try:
            request.headers['User-Agent'] = self.ua.random
        except Exception:
            # 如果获取随机UA失败，使用默认的
            request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        return None


class RetryMiddleware:
    """自定义重试中间件"""
    
    def __init__(self, max_retry_times=3):
        self.max_retry_times = max_retry_times
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            max_retry_times=crawler.settings.getint('RETRY_TIMES', 3)
        )
    
    def process_response(self, request, response, spider):
        """处理响应"""
        # 如果是429（太多请求），增加延迟后重试
        if response.status == 429:
            retry_times = request.meta.get('retry_times', 0) + 1
            
            if retry_times <= self.max_retry_times:
                spider.logger.warning(
                    f"收到429错误，等待后重试 (第{retry_times}次): {request.url}"
                )
                time.sleep(random.randint(5, 10))  # 等待5-10秒
                retryreq = request.copy()
                retryreq.meta['retry_times'] = retry_times
                return retryreq
        
        return response


class DataMergeMiddleware:
    """数据合并中间件
    
    用于合并来自不同数据源（百度百科和维基百科）的数据
    """
    
    def __init__(self):
        self.data_cache = {}  # 缓存已爬取的数据，用于合并
    
    def process_item(self, item, spider):
        """处理数据项，执行合并逻辑"""
        item_id = self._get_item_id(item)
        
        if not item_id:
            return item
        
        # 如果缓存中已有该条数据
        if item_id in self.data_cache:
            cached_item = self.data_cache[item_id]
            merged_item = self._merge_items(cached_item, item, spider)
            self.data_cache[item_id] = merged_item
            return merged_item
        else:
            # 首次遇到该数据，加入缓存
            self.data_cache[item_id] = item
            return item
    
    def _get_item_id(self, item):
        """获取数据项的ID"""
        if hasattr(item, 'emperor_id'):
            return item.emperor_id
        elif hasattr(item, 'event_id'):
            return item.event_id
        elif hasattr(item, 'person_id'):
            return item.person_id
        return None
    
    def _merge_items(self, item1, item2, spider):
        """合并两个数据项
        
        合并策略：
        1. 优先使用百度百科的结构化字段
        2. 使用维基百科补充详细描述
        3. 列表字段取并集
        """
        # 确定哪个是百度数据，哪个是维基数据
        baidu_item = item1 if item1.data_source == 'baidu' else item2
        wiki_item = item1 if item1.data_source == 'wikipedia' else item2
        
        # 以百度数据为基础
        merged = baidu_item
        
        # 补充维基数据中的空缺字段
        for field_name in dir(merged):
            if field_name.startswith('_'):
                continue
            
            merged_value = getattr(merged, field_name, None)
            wiki_value = getattr(wiki_item, field_name, None)
            
            # 如果百度数据的字段为空，使用维基数据
            if not merged_value and wiki_value:
                setattr(merged, field_name, wiki_value)
            
            # 对于文本字段，如果维基的更详细，使用维基的
            elif field_name in ['biography', 'description', 'achievements']:
                if wiki_value and len(str(wiki_value)) > len(str(merged_value or '')):
                    setattr(merged, field_name, wiki_value)
            
            # 对于列表字段，取并集
            elif field_name in ['alias', 'works', 'related_persons', 'related_emperors']:
                if isinstance(merged_value, list) and isinstance(wiki_value, list):
                    combined = list(set(merged_value + wiki_value))
                    setattr(merged, field_name, combined)
        
        # 更新数据来源标记
        merged.data_source = 'baidu,wikipedia'
        
        spider.logger.info(f"合并数据: {self._get_item_id(merged)}")
        
        return merged
