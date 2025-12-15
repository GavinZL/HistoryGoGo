"""
明朝皇帝爬虫 - 基于千问大模型的智能化爬虫
爬取 Wikipedia 和百度百科的 HTML 页面，然后由千问大模型进行结构化提取
"""

import scrapy
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

from crawler_new.models.items import HtmlPageItem, LinkItem
from crawler_new.config.ming_data import MING_EMPERORS, MING_DYNASTY


class MingEmperorSpider(scrapy.Spider):
    """明朝皇帝爬虫"""
    
    name = 'ming_emperor'
    
    # 允许的域名
    allowed_domains = ['zh.wikipedia.org', 'baike.baidu.com']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def __init__(self, source='both', *args, **kwargs):
        """
        初始化爬虫
        
        Args:
            source: 数据源选择，可选值：'wikipedia', 'baidu', 'both'（默认）
        """
        super().__init__(*args, **kwargs)
        self.data_source = source
        self.crawled_urls = set()  # 防止重复爬取
        
    def start_requests(self):
        """生成起始请求"""
        # 从 settings 中获取爬取模式配置
        crawl_mode = self.settings.get('CRAWL_MODE', 'test')
        test_emperor_count = self.settings.get('TEST_EMPEROR_COUNT', 3)
        
        self.logger.info(f"\n{'='*100}")
        self.logger.info(f"🚀 [爬虫启动] Spider: {self.name}")
        self.logger.info(f"   数据源: {self.data_source}")
        self.logger.info(f"   爬取模式: {crawl_mode}")
        self.logger.info(f"{'='*100}\n")
        
        # 根据爬取模式决定爬取多少位皇帝
        emperors_to_crawl = MING_EMPERORS
        if crawl_mode == 'test':
            emperors_to_crawl = MING_EMPERORS[:test_emperor_count]
            self.logger.info(f"📋 [爬取范围] 测试模式：只爬取前 {test_emperor_count} 位皇帝")
        else:
            self.logger.info(f"📋 [爬取范围] 全量模式：爬取所有 {len(MING_EMPERORS)} 位皇帝")
        
        self.logger.info(f"📊 [统计] 待爬取皇帝: {len(emperors_to_crawl)} 位")
        for idx, emp in enumerate(emperors_to_crawl, 1):
            self.logger.info(f"   {idx}. {emp['name']} ({emp['temple_name']}) - {emp['reign_title']}")
        self.logger.info("")
        
        # 爬取皇帝信息
        request_count = 0
        for emperor_info in emperors_to_crawl:
            # 根据 source 参数决定爬取哪个数据源
            if self.data_source in ['wikipedia', 'both']:
                request_count += 1
                yield self._create_request(
                    url=emperor_info['wikipedia_url'],
                    emperor_info=emperor_info,
                    data_source='wikipedia'
                )
            
            if self.data_source in ['baidu', 'both']:
                request_count += 1
                yield self._create_request(
                    url=emperor_info['baidu_url'],
                    emperor_info=emperor_info,
                    data_source='baidu'
                )
        
        self.logger.info(f"✅ [请求生成] 共生成 {request_count} 个爬取请求\n")
    
    def _create_request(self, url: str, emperor_info: dict, data_source: str):
        """创建请求"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"👑 [请求创建] 皇帝: {emperor_info['name']} ({data_source})")
        self.logger.info(f"   URL: {url}")
        self.logger.info(f"   朝代顺序: {emperor_info.get('dynasty_order')}")
        self.logger.info(f"   庙号: {emperor_info.get('temple_name')}")
        self.logger.info(f"   年号: {emperor_info.get('reign_title')}")
        self.logger.info(f"{'='*80}")
        
        return scrapy.Request(
            url=url,
            callback=self.parse_emperor,
            meta={
                'emperor_info': emperor_info,
                'data_source': data_source,
                'page_type': 'emperor',
                'depth': 0  # 递归深度
            },
            dont_filter=True
        )
    
    def parse_emperor(self, response):
        """解析皇帝页面 - 只保存 HTML，不做解析"""
        emperor_info = response.meta['emperor_info']
        data_source = response.meta['data_source']
        page_name = emperor_info['name']
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"✅ [HTTP响应] 成功获取HTML")
        self.logger.info(f"   皇帝: {page_name}")
        self.logger.info(f"   数据源: {data_source}")
        self.logger.info(f"   状态码: {response.status}")
        self.logger.info(f"   HTML大小: {len(response.text)} 字符")
        self.logger.info(f"{'='*80}")
        
        # 标记已爬取
        self.crawled_urls.add(response.url)
        
        # 生成页面ID
        page_id = f"ming_emperor_{emperor_info['dynasty_order']:03d}_{data_source}"
        
        self.logger.info(f"📦 [Item创建] 生成 HtmlPageItem")
        self.logger.info(f"   page_id: {page_id}")
        self.logger.info(f"   page_type: emperor")
        self.logger.info(f"   page_name: {page_name}")
        
        # 创建 HtmlPageItem
        html_item = HtmlPageItem(
            page_type='emperor',
            page_id=page_id,
            page_name=page_name,
            data_source=data_source,
            source_url=response.url,
            html_content=response.text,
            metadata={
                'temple_name': emperor_info.get('temple_name'),
                'reign_title': emperor_info.get('reign_title'),
                'dynasty_order': emperor_info['dynasty_order'],
                'reign_years': emperor_info.get('reign_years'),
                'dynasty_id': MING_DYNASTY['dynasty_id']
            },
            crawl_time=datetime.now().isoformat()
        )
        
        self.logger.info(f"➡️  [Pipeline] 提交 HtmlPageItem 到 Pipeline 处理链\n")
        
        # 提交 Item 到 Pipeline
        yield html_item
    
    def parse_event(self, response):
        """解析事件页面"""
        event_name = response.meta['event_name']
        data_source = response.meta['data_source']
        depth = response.meta.get('depth', 1)
        
        # 防止重复爬取
        if response.url in self.crawled_urls:
            self.logger.info(f"⚠️  [去重] 事件页面已爬取，跳过: {event_name}")
            return
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📰 [事件爬取] 成功获取事件HTML")
        self.logger.info(f"   事件: {event_name}")
        self.logger.info(f"   数据源: {data_source}")
        self.logger.info(f"   递归深度: {depth}")
        self.logger.info(f"   状态码: {response.status}")
        self.logger.info(f"   HTML大小: {len(response.text)} 字符")
        self.logger.info(f"{'='*80}")
        
        self.crawled_urls.add(response.url)
        
        # 生成页面ID
        page_id = f"ming_event_{event_name}_{data_source}"
        
        # 创建 HtmlPageItem
        html_item = HtmlPageItem(
            page_type='event',
            page_id=page_id,
            page_name=event_name,
            data_source=data_source,
            source_url=response.url,
            html_content=response.text,
            metadata={
                'dynasty_id': MING_DYNASTY['dynasty_id'],
                'depth': depth,
                'source_page': response.meta.get('source_page', '')
            },
            crawl_time=datetime.now().isoformat()
        )
        
        yield html_item
    
    def parse_person(self, response):
        """解析人物页面"""
        person_name = response.meta['person_name']
        data_source = response.meta['data_source']
        depth = response.meta.get('depth', 1)
        
        # 防止重复爬取
        if response.url in self.crawled_urls:
            self.logger.info(f"⚠️  [去重] 人物页面已爬取，跳过: {person_name}")
            return
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"👤 [人物爬取] 成功获取人物HTML")
        self.logger.info(f"   人物: {person_name}")
        self.logger.info(f"   数据源: {data_source}")
        self.logger.info(f"   递归深度: {depth}")
        self.logger.info(f"   状态码: {response.status}")
        self.logger.info(f"   HTML大小: {len(response.text)} 字符")
        self.logger.info(f"{'='*80}")
        
        self.crawled_urls.add(response.url)
        
        # 生成页面ID
        page_id = f"ming_person_{person_name}_{data_source}"
        
        # 创建 HtmlPageItem
        html_item = HtmlPageItem(
            page_type='person',
            page_id=page_id,
            page_name=person_name,
            data_source=data_source,
            source_url=response.url,
            html_content=response.text,
            metadata={
                'dynasty_id': MING_DYNASTY['dynasty_id'],
                'depth': depth,
                'source_page': response.meta.get('source_page', '')
            },
            crawl_time=datetime.now().isoformat()
        )
        
        yield html_item
