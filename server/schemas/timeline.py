"""
时间轴相关Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class TimelineEvent(BaseModel):
    """时间轴事件"""
    event_id: str
    title: str
    event_type: str
    start_date: date
    location: Optional[str] = None


class TimelineEmperor(BaseModel):
    """时间轴皇帝信息"""
    emperor_id: str
    name: str
    temple_name: Optional[str] = None
    reign_title: Optional[str] = None
    reign_year: int = Field(..., description="在位第几年")


class TimelineItem(BaseModel):
    """时间线项"""
    year: int = Field(..., description="年份")
    events: List[TimelineEvent] = Field(default_factory=list, description="该年发生的事件")
    emperor: Optional[TimelineEmperor] = Field(None, description="当年在位皇帝")


class TimelineResponse(BaseModel):
    """时间轴响应"""
    dynasty_id: str
    dynasty_name: str
    start_year: int
    end_year: int
    timeline: List[TimelineItem] = Field(..., description="时间线数据")
    total_events: int = Field(..., description="事件总数")
    total_emperors: int = Field(..., description="皇帝总数")
