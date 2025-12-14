"""
皇帝相关Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class EmperorBase(BaseModel):
    """皇帝基础Schema"""
    name: str = Field(..., description="姓名")
    temple_name: Optional[str] = Field(None, description="庙号")
    reign_title: Optional[str] = Field(None, description="年号")
    dynasty_order: int = Field(..., description="朝代顺序")


class EmperorResponse(EmperorBase):
    """皇帝响应Schema"""
    emperor_id: str = Field(..., description="皇帝ID")
    dynasty_id: str = Field(..., description="朝代ID")
    birth_date: Optional[date] = Field(None, description="出生日期")
    death_date: Optional[date] = Field(None, description="去世日期")
    reign_start: date = Field(..., description="在位开始日期")
    reign_end: Optional[date] = Field(None, description="在位结束日期")
    reign_duration: Optional[int] = Field(None, description="在位年数")
    biography: Optional[str] = Field(None, description="生平简介")
    achievements: Optional[str] = Field(None, description="主要成就")
    portrait_url: Optional[str] = Field(None, description="画像URL")
    data_source: str = Field(..., description="数据来源")
    
    class Config:
        from_attributes = True


class EmperorSummary(BaseModel):
    """皇帝摘要Schema（用于列表）"""
    emperor_id: str
    name: str
    temple_name: Optional[str] = None
    reign_title: Optional[str] = None
    reign_start: date
    reign_end: Optional[date] = None
    reign_duration: Optional[int] = None
    dynasty_order: int
    portrait_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class EmperorDetail(EmperorResponse):
    """皇帝详情Schema"""
    event_count: Optional[int] = Field(None, description="相关事件数量")
    person_count: Optional[int] = Field(None, description="相关人物数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
