"""
HTML内容存储Pipeline
用于存储人物生平、事迹等HTML原始内容
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class HtmlStoragePipeline:
    """HTML内容存储Pipeline"""
    
    def __init__(self, storage_base_path: str):
        self.storage_base_path = storage_base_path
        self.persons_dir = Path(storage_base_path) / 'person'
        self.emperors_dir = Path(storage_base_path) / 'emperor'
        self.events_dir = Path(storage_base_path) / 'event'
        
    @classmethod
    def from_crawler(cls, crawler):
        storage_path = crawler.settings.get('HTML_STORAGE_PATH', 'crawler/data/html')
        return cls(storage_base_path=storage_path)
    
    def open_spider(self, spider):
        """爬虫启动时创建存储目录"""
        self.persons_dir.mkdir(parents=True, exist_ok=True)
        self.emperors_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        spider.logger.info(f"[HtmlStorage] 创建HTML存储目录: {self.storage_base_path}")
    
    def process_item(self, item, spider):
        """处理Item并存储HTML内容"""
        # 检查item中是否包含html_content字段
        if hasattr(item, 'html_content') and item.html_content:
            self._save_html_content(item, spider)
        
        return item
    
    def _save_html_content(self, item, spider):
        """保存HTML内容到文件"""
        try:
            # 根据item类型确定存储目录
            item_type = item.__class__.__name__.lower()
            
            if item_type == 'person':
                save_dir = self.persons_dir
                item_id = item.person_id
                name = item.name
            elif item_type == 'emperor':
                save_dir = self.emperors_dir
                item_id = item.emperor_id
                name = item.name
            elif item_type == 'event':
                save_dir = self.events_dir
                item_id = item.event_id
                name = item.title
            else:
                spider.logger.warning(f"[HtmlStorage] 未知的item类型: {item_type}")
                return
            
            # 创建文件名（使用ID和名称）
            safe_name = self._sanitize_filename(name)
            file_prefix = f"{safe_name}_{item_id}"
            
            # 保存HTML内容
            html_file = save_dir / f"{file_prefix}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(item.html_content)
            
            # 保存元数据
            metadata = {
                'item_id': item_id,
                'name': name,
                'data_source': getattr(item, 'data_source', 'unknown'),
                'crawl_time': datetime.now().isoformat(),
                'url': getattr(item, 'source_url', ''),
            }
            
            metadata_file = save_dir / f"{file_prefix}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            spider.logger.info(f"[HtmlStorage] 保存HTML内容: {html_file}")
            
        except Exception as e:
            spider.logger.error(f"[HtmlStorage] 保存HTML内容失败: {str(e)}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        # 移除文件系统不允许的字符
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 限制文件名长度
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename
    
    def close_spider(self, spider):
        """爬虫关闭时的清理工作"""
        spider.logger.info("[HtmlStorage] HTML存储Pipeline关闭")
