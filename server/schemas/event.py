"""
事件相关Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class EventBase(BaseModel):
    """事件基础Schema"""
    title: str = Field(..., description="事件标题")
    event_type: str = Field(..., description="事件类型")
    start_date: date = Field(..., description="开始日期")


class EventResponse(EventBase):
    """事件响应Schema"""
    event_id: str = Field(..., description="事件ID")
    dynasty_id: str = Field(..., description="朝代ID")
    emperor_id: Optional[str] = Field(None, description="关联皇帝ID")
    end_date: Optional[date] = Field(None, description="结束日期")
    location: Optional[str] = Field(None, description="发生地点")
    description: Optional[str] = Field(None, description="事件描述")
    significance: Optional[str] = Field(None, description="历史意义")
    data_source: str = Field(..., description="数据来源")
    
    class Config:
        from_attributes = True


class EventSummary(BaseModel):
    """事件摘要Schema（用于列表）"""
    event_id: str
    title: str
    event_type: str
    start_date: date
    end_date: Optional[date] = None
    location: Optional[str] = None
    
    class Config:
        from_attributes = True


class EventDetail(EventResponse):
    """事件详情Schema"""
    participants: Optional[str] = Field(None, description="参与者")
    casualties: Optional[str] = Field(None, description="伤亡情况")
    result: Optional[str] = Field(None, description="事件结果")
    related_persons: Optional[List[str]] = Field(default_factory=list, description="相关人物ID列表")
    person_count: Optional[int] = Field(0, description="相关人物数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
