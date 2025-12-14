"""
数据实体模型定义
定义皇帝、事件、人物等实体的数据结构
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List
from enum import Enum


class EventType(Enum):
    """事件类型枚举"""
    POLITICAL = "political"  # 政治事件
    MILITARY = "military"  # 军事事件
    CULTURAL = "cultural"  # 文化事件
    ECONOMIC = "economic"  # 经济事件
    DIPLOMATIC = "diplomatic"  # 外交事件
    NATURAL = "natural"  # 自然灾害
    TECHNOLOGICAL = "technological"  # 科技事件


class PersonType(Enum):
    """人物类型枚举"""
    OFFICIAL = "official"  # 文臣
    GENERAL = "general"  # 武将
    WRITER = "writer"  # 文学家
    ARTIST = "artist"  # 艺术家
    THINKER = "thinker"  # 思想家
    SCIENTIST = "scientist"  # 科学家
    ROYAL = "royal"  # 宗室
    MONK = "monk"  # 僧侣
    MERCHANT = "merchant"  # 商人
    OTHER = "other"  # 其他


@dataclass
class Dynasty:
    """朝代实体"""
    dynasty_id: str
    name: str
    start_year: int
    end_year: int
    capital: Optional[str] = None
    founder: Optional[str] = None
    description: Optional[str] = None
    data_source: str = "baidu"


@dataclass
class Emperor:
    """皇帝实体"""
    emperor_id: str
    dynasty_id: str
    name: str
    reign_start: date
    dynasty_order: int
    temple_name: Optional[str] = None
    reign_title: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    reign_end: Optional[date] = None
    reign_duration: Optional[int] = None
    biography: Optional[str] = None
    achievements: Optional[str] = None
    portrait_url: Optional[str] = None
    data_source: str = "baidu"

    def __post_init__(self):
        """计算在位年数"""
        if self.reign_end and self.reign_start:
            self.reign_duration = (self.reign_end - self.reign_start).days // 365


@dataclass
class Event:
    """事件实体"""
    event_id: str
    dynasty_id: str
    title: str
    event_type: EventType
    start_date: date
    emperor_id: Optional[str] = None
    end_date: Optional[date] = None
    location: Optional[str] = None
    description: Optional[str] = None
    significance: Optional[str] = None
    casualty: Optional[str] = None
    result: Optional[str] = None
    related_persons: List[str] = field(default_factory=list)
    data_source: str = "baidu"


@dataclass
class Person:
    """人物实体"""
    person_id: str
    dynasty_id: str
    name: str
    person_type: PersonType
    alias: List[str] = field(default_factory=list)
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    position: Optional[str] = None
    biography: Optional[str] = None
    style: Optional[str] = None
    works: List[str] = field(default_factory=list)
    contributions: Optional[str] = None
    portrait_url: Optional[str] = None
    related_emperors: List[str] = field(default_factory=list)
    data_source: str = "baidu"


@dataclass
class Work:
    """作品实体"""
    work_id: str
    person_id: str
    title: str
    work_type: Optional[str] = None  # 诗词/书法/绘画/著作
    creation_date: Optional[date] = None
    description: Optional[str] = None
    content: Optional[str] = None  # 作品内容（诗词全文等）
    image_url: Optional[str] = None


@dataclass
class PersonRelation:
    """人物关系实体"""
    relation_id: str
    person_id_from: str
    person_id_to: str
    relation_type: str  # 师生/君臣/父子/好友等
    description: Optional[str] = None
