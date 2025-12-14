"""
SQLite持久化管道
将爬取的数据保存到SQLite数据库
"""

import json
from typing import Any
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crawler.models.entities import Emperor, Event, Person, Work
from server.database.sqlite_manager import SQLiteManager


class SQLitePipeline:
    """SQLite数据持久化管道"""
    
    def __init__(self, db_path: str = None):
        self.db_manager = SQLiteManager(db_path)
        self.stats = {
            'emperors': 0,
            'events': 0,
            'persons': 0,
            'works': 0,
            'errors': 0
        }
    
    def open_spider(self, spider):
        """爬虫启动时初始化数据库"""
        try:
            # 确保数据库已初始化
            if not self.db_manager.db_path.exists():
                spider.logger.info("💾 数据库不存在，正在初始化...")
                self.db_manager.initialize_database()
                spider.logger.info("✅ 数据库初始化成功")
            else:
                # 连接现有数据库
                self.db_manager.connect()
                spider.logger.info(f"💾 SQLite管道已连接: {self.db_manager.db_path}")
        except Exception as e:
            spider.logger.error(f"❌ 数据库初始化失败: {str(e)}")
            raise
    
    def close_spider(self, spider):
        """爬虫关闭时输出统计并关闭连接"""
        spider.logger.info("\n" + "="*80)
        spider.logger.info("💾 SQLite持久化统计")
        spider.logger.info("="*80)
        spider.logger.info(
            f"皇帝={self.stats['emperors']}, "
            f"事件={self.stats['events']}, "
            f"人物={self.stats['persons']}, "
            f"作品={self.stats['works']}, "
            f"错误={self.stats['errors']}"
        )
        
        total_saved = self.stats['emperors'] + self.stats['events'] + self.stats['persons'] + self.stats['works']
        spider.logger.info(f"总计保存: {total_saved} 条数据")
        
        if self.stats['errors'] > 0:
            spider.logger.warning(f"⚠️ 有 {self.stats['errors']} 条数据保存失败")
        else:
            spider.logger.info("✅ 所有数据均成功保存")
        
        spider.logger.info(f"数据库位置: {self.db_manager.db_path}")
        spider.logger.info("="*80 + "\n")
        
        self.db_manager.close()
    
    def process_item(self, item: Any, spider):
        """处理数据项"""
        try:
            if isinstance(item, Emperor):
                self._save_emperor(item, spider)
                self.stats['emperors'] += 1
            elif isinstance(item, Event):
                self._save_event(item, spider)
                self.stats['events'] += 1
            elif isinstance(item, Person):
                self._save_person(item, spider)
                self.stats['persons'] += 1
            elif isinstance(item, Work):
                self._save_work(item, spider)
                self.stats['works'] += 1
            else:
                spider.logger.warning(f"未知的数据类型: {type(item)}")
            
            return item
        
        except Exception as e:
            self.stats['errors'] += 1
            spider.logger.error(f"数据保存失败: {str(e)}")
            return item
    
    def _save_emperor(self, emperor: Emperor, spider):
        """保存皇帝数据"""
        sql = """
        INSERT OR REPLACE INTO emperors (
            emperor_id, dynasty_id, name, temple_name, reign_title,
            birth_date, death_date, reign_start, reign_end, reign_duration,
            dynasty_order, biography, achievements, portrait_url, data_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            emperor.emperor_id,
            emperor.dynasty_id,
            emperor.name,
            emperor.temple_name,
            emperor.reign_title,
            emperor.birth_date.isoformat() if emperor.birth_date else None,
            emperor.death_date.isoformat() if emperor.death_date else None,
            emperor.reign_start.isoformat() if emperor.reign_start else None,
            emperor.reign_end.isoformat() if emperor.reign_end else None,
            emperor.reign_duration,
            emperor.dynasty_order,
            emperor.biography,
            emperor.achievements,
            emperor.portrait_url,
            emperor.data_source
        )
        
        self.db_manager.execute(sql, params)
        spider.logger.debug(f"💾 已保存皇帝: {emperor.name}")
    
    def _save_event(self, event: Event, spider):
        """保存事件数据"""
        sql = """
        INSERT OR REPLACE INTO events (
            event_id, dynasty_id, emperor_id, title, event_type,
            start_date, end_date, location, description, significance,
            casualty, result, data_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            event.event_id,
            event.dynasty_id,
            event.emperor_id,
            event.title,
            event.event_type.value if event.event_type else None,
            event.start_date.isoformat() if event.start_date else None,
            event.end_date.isoformat() if event.end_date else None,
            event.location,
            event.description,
            event.significance,
            event.casualty,
            event.result,
            event.data_source
        )
        
        self.db_manager.execute(sql, params)
        spider.logger.debug(f"💾 已保存事件: {event.title}")
        
        # 保存事件-人物关联
        if event.related_persons:
            self._save_event_person_relations(event, spider)
    
    def _save_event_person_relations(self, event: Event, spider):
        """保存事件-人物关联关系"""
        for person_id in event.related_persons:
            sql = """
            INSERT OR IGNORE INTO event_person_relation (
                relation_id, event_id, person_id
            ) VALUES (?, ?, ?)
            """
            
            relation_id = f"{event.event_id}_{person_id}"
            params = (relation_id, event.event_id, person_id)
            
            try:
                self.db_manager.execute(sql, params)
            except Exception as e:
                spider.logger.debug(f"保存事件-人物关联失败: {str(e)}")
    
    def _save_person(self, person: Person, spider):
        """保存人物数据"""
        sql = """
        INSERT OR REPLACE INTO persons (
            person_id, dynasty_id, name, alias, birth_date, death_date,
            person_type, position, biography, style, contributions,
            portrait_url, data_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 将列表转换为JSON字符串
        alias_json = json.dumps(person.alias, ensure_ascii=False) if person.alias else None
        
        params = (
            person.person_id,
            person.dynasty_id,
            person.name,
            alias_json,
            person.birth_date.isoformat() if person.birth_date else None,
            person.death_date.isoformat() if person.death_date else None,
            person.person_type.value if person.person_type else None,
            person.position,
            person.biography,
            person.style,
            person.contributions,
            person.portrait_url,
            person.data_source
        )
        
        self.db_manager.execute(sql, params)
        spider.logger.debug(f"💾 已保存人物: {person.name}")
        
        # 保存作品
        if person.works:
            self._save_person_works(person, spider)
    
    def _save_person_works(self, person: Person, spider):
        """保存人物作品"""
        for work_title in person.works:
            sql = """
            INSERT OR IGNORE INTO works (
                work_id, person_id, title
            ) VALUES (?, ?, ?)
            """
            
            work_id = f"{person.person_id}_{hash(work_title) % 100000:05d}"
            params = (work_id, person.person_id, work_title)
            
            try:
                self.db_manager.execute(sql, params)
            except Exception as e:
                spider.logger.debug(f"保存作品失败: {str(e)}")
    
    def _save_work(self, work: Work, spider):
        """保存作品数据"""
        sql = """
        INSERT OR REPLACE INTO works (
            work_id, person_id, title, work_type, creation_date,
            description, content, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            work.work_id,
            work.person_id,
            work.title,
            work.work_type,
            work.creation_date.isoformat() if work.creation_date else None,
            work.description,
            work.content,
            work.image_url
        )
        
        self.db_manager.execute(sql, params)
        spider.logger.debug(f"已保存作品: {work.title}")
