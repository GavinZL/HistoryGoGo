"""
SQLite 存储 Pipeline
将提取的结构化数据存入 SQLite 数据库
"""

from crawler_new.models.items import ExtractedDataItem


class SQLitePipeline:
    """SQLite存储Pipeline"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    @classmethod
    def from_crawler(cls, crawler):
        db_path = crawler.settings.get('SQLITE_DB_PATH', 'server/database/historygogo.db')
        return cls(db_path)
    
    def open_spider(self, spider):
        """Spider 开启时连接数据库"""
        spider.logger.info(f"💾 SQLite Pipeline 已初始化: {self.db_path}")
        spider.logger.info("   （数据库存储功能待实现，需复用 crawler 的 SQLite Pipeline 逻辑）")
    
    def close_spider(self, spider):
        """Spider 关闭时断开数据库连接"""
        if self.conn:
            self.conn.close()
    
    def process_item(self, item, spider):
        """处理 Item"""
        # 只处理 ExtractedDataItem
        if not isinstance(item, ExtractedDataItem):
            return item
        
        try:
            # TODO: 实现数据库存储逻辑
            # 1. 解析 extracted_data
            # 2. 转换为 crawler.models.entities 中的数据模型
            # 3. 存入 SQLite 数据库
            
            spider.logger.info(f"💾 SQLite存储: {item['html_item']['page_id']}（待实现）")
            
        except Exception as e:
            spider.logger.error(f"❌ SQLite存储失败: {item['html_item']['page_id']}, 错误: {str(e)}")
        
        return item
