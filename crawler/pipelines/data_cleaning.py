"""
数据清洗管道
对爬取的原始数据进行清洗和标准化处理
"""

import re
from typing import Any
from crawler.models.entities import Emperor, Event, Person
from crawler.utils.date_utils import clean_text


class DataCleaningPipeline:
    """数据清洗管道"""
    
    def __init__(self):
        self.stats = {
            'processed': 0,
            'cleaned': 0,
            'errors': 0
        }
    
    def open_spider(self, spider):
        """爬虫启动时调用"""
        spider.logger.info("🧽 数据清洗管道已启动")
    
    def process_item(self, item: Any, spider):
        """处理数据项"""
        try:
            self.stats['processed'] += 1
            
            if isinstance(item, Emperor):
                cleaned_item = self._clean_emperor(item)
                spider.logger.debug(f"🧽 清洗皇帝数据: {item.name}")
            elif isinstance(item, Event):
                cleaned_item = self._clean_event(item)
                spider.logger.debug(f"🧽 清洗事件数据: {item.title}")
            elif isinstance(item, Person):
                cleaned_item = self._clean_person(item)
                spider.logger.debug(f"🧽 清洗人物数据: {item.name}")
            else:
                spider.logger.warning(f"未知的数据类型: {type(item)}")
                return item
            
            self.stats['cleaned'] += 1
            return cleaned_item
        
        except Exception as e:
            self.stats['errors'] += 1
            spider.logger.error(f"数据清洗失败: {str(e)}")
            return item
    
    def _clean_emperor(self, emperor: Emperor) -> Emperor:
        """清洗皇帝数据"""
        # 清洗文本字段
        if emperor.biography:
            emperor.biography = self._clean_and_truncate(emperor.biography, max_length=1000)
        
        if emperor.achievements:
            emperor.achievements = self._clean_and_truncate(emperor.achievements, max_length=500)
        
        # 清洗庙号和年号
        if emperor.temple_name:
            emperor.temple_name = clean_text(emperor.temple_name).strip()
        
        if emperor.reign_title:
            emperor.reign_title = clean_text(emperor.reign_title).strip()
        
        # 验证并清洗姓名
        emperor.name = self._clean_name(emperor.name)
        
        return emperor
    
    def _clean_event(self, event: Event) -> Event:
        """清洗事件数据"""
        # 清洗标题
        event.title = self._clean_name(event.title)
        
        # 清洗描述字段
        if event.description:
            event.description = self._clean_and_truncate(event.description, max_length=2000)
        
        if event.significance:
            event.significance = self._clean_and_truncate(event.significance, max_length=1000)
        
        if event.result:
            event.result = self._clean_and_truncate(event.result, max_length=500)
        
        # 清洗地点
        if event.location:
            event.location = clean_text(event.location).strip()
            # 移除过长的地点描述
            if len(event.location) > 50:
                event.location = event.location[:50]
        
        # 清洗相关人物列表
        if event.related_persons:
            event.related_persons = self._clean_list(event.related_persons)
        
        return event
    
    def _clean_person(self, person: Person) -> Person:
        """清洗人物数据"""
        # 清洗姓名
        person.name = self._clean_name(person.name)
        
        # 清洗别名列表
        if person.alias:
            person.alias = self._clean_list(person.alias)
            # 移除与主名称相同的别名
            person.alias = [a for a in person.alias if a != person.name]
        
        # 清洗文本字段
        if person.biography:
            person.biography = self._clean_and_truncate(person.biography, max_length=1500)
        
        if person.style:
            person.style = self._clean_and_truncate(person.style, max_length=500)
        
        if person.contributions:
            person.contributions = self._clean_and_truncate(person.contributions, max_length=1000)
        
        # 清洗职位
        if person.position:
            person.position = clean_text(person.position).strip()
            if len(person.position) > 100:
                person.position = person.position[:100]
        
        # 清洗作品列表
        if person.works:
            person.works = self._clean_list(person.works)
        
        # 清洗关联皇帝列表
        if person.related_emperors:
            person.related_emperors = self._clean_list(person.related_emperors)
        
        return person
    
    def _clean_and_truncate(self, text: str, max_length: int = 1000) -> str:
        """清洗并截断文本"""
        if not text:
            return ""
        
        # 基本清洗
        text = clean_text(text)
        
        # 移除多余的标点符号
        text = re.sub(r'[。，、]{2,}', '，', text)
        
        # 移除多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        # 截断过长的文本
        if len(text) > max_length:
            # 尝试在句号处截断
            truncated = text[:max_length]
            last_period = truncated.rfind('。')
            if last_period > max_length * 0.8:  # 如果最后一个句号位置合理
                text = truncated[:last_period + 1]
            else:
                text = truncated + '...'
        
        return text.strip()
    
    def _clean_name(self, name: str) -> str:
        """清洗名称"""
        if not name:
            return ""
        
        # 基本清洗
        name = clean_text(name).strip()
        
        # 移除括号内的注释（如"朱元璋(明太祖)"）
        name = re.sub(r'[（(].*?[）)]', '', name)
        
        # 移除前后空格
        name = name.strip()
        
        # 如果名称过长（可能包含描述），只保留前面部分
        if len(name) > 20:
            name = name[:20]
        
        return name
    
    def _clean_list(self, items: list) -> list:
        """清洗列表"""
        if not items:
            return []
        
        # 清洗每个元素
        cleaned = []
        for item in items:
            if isinstance(item, str):
                cleaned_item = clean_text(item).strip()
                if cleaned_item and len(cleaned_item) <= 100:  # 移除过长或空的元素
                    cleaned.append(cleaned_item)
            else:
                cleaned.append(item)
        
        # 去重并保持顺序
        seen = set()
        unique_list = []
        for item in cleaned:
            if item not in seen:
                seen.add(item)
                unique_list.append(item)
        
        return unique_list
    
    def close_spider(self, spider):
        """爬虫关闭时输出统计信息"""
        spider.logger.info(
            f"🧽 数据清洗统计: 处理={self.stats['processed']}, "
            f"清洗={self.stats['cleaned']}, 错误={self.stats['errors']}"
        )
        
        if self.stats['processed'] > 0:
            clean_rate = (self.stats['cleaned'] / self.stats['processed']) * 100
            spider.logger.info(f"   清洗成功率: {clean_rate:.2f}%")
