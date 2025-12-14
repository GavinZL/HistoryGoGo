"""
人物相关Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class PersonBase(BaseModel):
    """人物基础Schema"""
    name: str = Field(..., description="姓名")
    person_type: str = Field(..., description="人物类型")


class PersonResponse(PersonBase):
    """人物响应Schema"""
    person_id: str = Field(..., description="人物ID")
    dynasty_id: str = Field(..., description="朝代ID")
    alias: Optional[List[str]] = Field(None, description="别名、字号")
    birth_date: Optional[date] = Field(None, description="出生日期")
    death_date: Optional[date] = Field(None, description="去世日期")
    position: Optional[str] = Field(None, description="主要职位")
    biography: Optional[str] = Field(None, description="生平简介")
    contributions: Optional[str] = Field(None, description="主要贡献")
    portrait_url: Optional[str] = Field(None, description="画像URL")
    data_source: str = Field(..., description="数据来源")
    
    class Config:
        from_attributes = True


class PersonSummary(BaseModel):
    """人物摘要Schema（用于列表）"""
    person_id: str
    name: str
    person_type: str
    alias: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    dynasty_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class PersonDetail(PersonResponse):
    """人物详情Schema"""
    style: Optional[str] = Field(None, description="风格特点")
    works: Optional[List[str]] = Field(default_factory=list, description="作品列表")
    related_emperors: Optional[List[str]] = Field(default_factory=list, description="相关皇帝ID列表")
    achievements: Optional[str] = Field(None, description="主要成就")
    event_count: Optional[int] = Field(0, description="参与事件数量")
    work_count: Optional[int] = Field(0, description="作品数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
