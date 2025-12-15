"""
Neo4j 存储 Pipeline
将提取的结构化数据存入 Neo4j 图数据库
"""

from crawler_new.models.items import ExtractedDataItem


class Neo4jPipeline:
    """Neo4j存储Pipeline"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    @classmethod
    def from_crawler(cls, crawler):
        uri = crawler.settings.get('NEO4J_URI', 'bolt://localhost:7687')
        user = crawler.settings.get('NEO4J_USER', 'neo4j')
        password = crawler.settings.get('NEO4J_PASSWORD', '')
        return cls(uri, user, password)
    
    def open_spider(self, spider):
        """Spider 开启时连接 Neo4j"""
        spider.logger.info(f"🔗 Neo4j Pipeline 已初始化: {self.uri}")
        spider.logger.info("   （图数据库存储功能待实现，需复用 crawler 的 Neo4j Pipeline 逻辑）")
    
    def close_spider(self, spider):
        """Spider 关闭时断开连接"""
        if self.driver:
            self.driver.close()
    
    def process_item(self, item, spider):
        """处理 Item"""
        # 只处理 ExtractedDataItem
        if not isinstance(item, ExtractedDataItem):
            return item
        
        try:
            # TODO: 实现 Neo4j 存储逻辑
            # 1. 解析 extracted_data
            # 2. 创建节点和关系
            # 3. 存入 Neo4j
            
            spider.logger.info(f"🔗 Neo4j存储: {item['html_item']['page_id']}（待实现）")
            
        except Exception as e:
            spider.logger.error(f"❌ Neo4j存储失败: {item['html_item']['page_id']}, 错误: {str(e)}")
        
        return item
