"""
HTML 存储 Pipeline
将爬取的原始 HTML 保存到本地文件系统
"""

import os
import json
from pathlib import Path
from datetime import datetime

from crawler_new.models.items import HtmlPageItem


class HtmlStoragePipeline:
    """HTML存储Pipeline"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        
    @classmethod
    def from_crawler(cls, crawler):
        storage_path = crawler.settings.get('HTML_STORAGE_PATH', 'crawler_new/data/html')
        return cls(storage_path)
    
    def open_spider(self, spider):
        """Spider 开启时创建存储目录"""
        spider.logger.info(f"\n{'='*100}")
        spider.logger.info(f"📁 [Pipeline-1] HtmlStoragePipeline 启动")
        spider.logger.info(f"   存储路径: {self.storage_path}")
        
        # 创建存储目录结构
        for subdir in ['emperor', 'event', 'person']:
            dir_path = Path(self.storage_path) / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
            spider.logger.info(f"   ✅ 目录已就绪: {dir_path}")
        
        spider.logger.info(f"{'='*100}\n")
    
    def process_item(self, item, spider):
        """处理 Item"""
        # 只处理 HtmlPageItem
        if not isinstance(item, HtmlPageItem):
            return item
        
        spider.logger.info(f"\n{'='*80}")
        spider.logger.info(f"💾 [Pipeline-1] HTML存储开始")
        spider.logger.info(f"   page_id: {item['page_id']}")
        spider.logger.info(f"   page_name: {item['page_name']}")
        spider.logger.info(f"   data_source: {item['data_source']}")
        spider.logger.info(f"   HTML大小: {len(item['html_content'])} 字符")
        
        try:
            # 保存 HTML 文件
            html_file = self._save_html(item, spider)
            spider.logger.info(f"   ✅ HTML文件: {html_file}")
            
            # 保存元数据
            metadata_file = self._save_metadata(item, spider)
            spider.logger.info(f"   ✅ 元数据文件: {metadata_file}")
            
            spider.logger.info(f"✅ [Pipeline-1] HTML存储完成")
            spider.logger.info(f"{'='*80}\n")
            
        except Exception as e:
            spider.logger.error(f"\n{'='*80}")
            spider.logger.error(f"❌ [Pipeline-1] HTML存储失败")
            spider.logger.error(f"   page_id: {item['page_id']}")
            spider.logger.error(f"   错误: {str(e)}")
            spider.logger.error(f"{'='*80}\n")
            import traceback
            spider.logger.debug(traceback.format_exc())
        
        return item
    
    def _save_html(self, item: HtmlPageItem, spider):
        """保存 HTML 文件"""
        # 构建文件路径
        page_type = item['page_type']
        page_id = item['page_id']
        
        file_path = Path(self.storage_path) / page_type / f"{page_id}.html"
        
        # 写入 HTML 内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(item['html_content'])
        
        return file_path
    
    def _save_metadata(self, item: HtmlPageItem, spider):
        """保存元数据 JSON 文件"""
        page_type = item['page_type']
        page_id = item['page_id']
        
        file_path = Path(self.storage_path) / page_type / f"{page_id}_metadata.json"
        
        # 构建元数据
        metadata = {
            'page_type': item['page_type'],
            'page_id': item['page_id'],
            'page_name': item['page_name'],
            'data_source': item['data_source'],
            'source_url': item['source_url'],
            'crawl_time': item['crawl_time'],
            'metadata': item['metadata']
        }
        
        # 写入 JSON 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return file_path
