"""
递归爬取 Pipeline
根据提取的链接自动触发新的爬取任务
"""

import scrapy
from crawler_new.models.items import ExtractedDataItem


class RecursiveCrawlPipeline:
    """递归爬取Pipeline"""
    
    def __init__(self, enable_recursive: bool, max_depth: int):
        self.enable_recursive = enable_recursive
        self.max_depth = max_depth
        self.crawled_urls = set()
    
    @classmethod
    def from_crawler(cls, crawler):
        enable_recursive = crawler.settings.get('ENABLE_RECURSIVE_CRAWL', True)
        max_depth = crawler.settings.get('MAX_RECURSIVE_DEPTH', 2)
        return cls(enable_recursive, max_depth)
    
    def open_spider(self, spider):
        """Spider 开启时初始化"""
        if self.enable_recursive:
            spider.logger.info(f"🔄 递归爬取已启用，最大深度: {self.max_depth}")
        else:
            spider.logger.info("🔄 递归爬取已禁用")
    
    def process_item(self, item, spider):
        """处理 Item"""
        # 只处理 ExtractedDataItem
        if not isinstance(item, ExtractedDataItem):
            return item
        
        # 如果未启用递归爬取，直接返回
        if not self.enable_recursive:
            return item
        
        try:
            # 获取当前深度
            current_depth = item['html_item']['metadata'].get('depth', 0)
            
            # 检查深度限制
            if current_depth >= self.max_depth:
                spider.logger.info(f"⚠️  已达最大递归深度 {self.max_depth}，停止递归")
                return item
            
            # 提取链接
            extracted_links = item.get('extracted_links', [])
            
            if extracted_links:
                spider.logger.info(f"🔗 发现 {len(extracted_links)} 个链接，准备递归爬取（深度: {current_depth + 1}）")
                
                # 为每个链接生成新的请求
                for link in extracted_links:
                    self._create_recursive_request(link, spider, current_depth + 1)
            
        except Exception as e:
            spider.logger.error(f"❌ 递归爬取处理失败: {str(e)}")
            import traceback
            spider.logger.debug(traceback.format_exc())
        
        return item
    
    def _create_recursive_request(self, link: dict, spider, depth: int):
        """创建递归请求"""
        link_url = link.get('url')
        link_type = link.get('type')  # event 或 person
        link_name = link.get('name')
        
        # 防止重复爬取
        if link_url in self.crawled_urls:
            spider.logger.debug(f"   ⚠️  链接已爬取，跳过: {link_name}")
            return
        
        # 检查URL是否有效
        if not link_url or link_url == 'null':
            return
        
        # 标记已爬取
        self.crawled_urls.add(link_url)
        
        spider.logger.info(f"   📥 添加递归请求: {link_type} - {link_name}（深度: {depth}）")
        
        # 构建请求
        if link_type == 'event':
            callback = spider.parse_event
            meta = {
                'event_name': link_name,
                'data_source': link.get('source', 'wikipedia'),
                'depth': depth,
                'source_page': spider.name
            }
        elif link_type == 'person':
            callback = spider.parse_person
            meta = {
                'person_name': link_name,
                'data_source': link.get('source', 'wikipedia'),
                'depth': depth,
                'source_page': spider.name
            }
        else:
            spider.logger.warning(f"   ⚠️  未知链接类型: {link_type}")
            return
        
        # 创建请求并提交到调度器
        request = scrapy.Request(
            url=link_url,
            callback=callback,
            meta=meta,
            dont_filter=False
        )
        
        # 将请求添加到爬虫的请求队列
        spider.crawler.engine.crawl(request, spider)
