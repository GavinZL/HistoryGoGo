"""
朝代相关Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DynastyBase(BaseModel):
    """朝代基础Schema"""
    name: str = Field(..., description="朝代名称")
    start_year: int = Field(..., description="开始年份")
    end_year: int = Field(..., description="结束年份")
    capital: Optional[str] = Field(None, description="都城")
    founder: Optional[str] = Field(None, description="开国皇帝")
    description: Optional[str] = Field(None, description="朝代描述")


class DynastyResponse(DynastyBase):
    """朝代响应Schema"""
    dynasty_id: str = Field(..., description="朝代ID")
    data_source: str = Field(..., description="数据来源")
    emperor_count: Optional[int] = Field(None, description="皇帝数量")
    
    class Config:
        from_attributes = True


class DynastyDetail(DynastyResponse):
    """朝代详情Schema"""
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
