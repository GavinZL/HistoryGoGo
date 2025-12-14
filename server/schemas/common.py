"""
通用Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import date

T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(20, ge=1, le=100, description="每页数量，最大100")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: List[T] = Field(..., description="数据列表")


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
