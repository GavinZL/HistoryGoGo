"""
朝代API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from server.schemas.dynasty import DynastyResponse, DynastyDetail
from server.schemas.common import PaginatedResponse, SuccessResponse
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


@router.get("/", response_model=List[DynastyResponse])
async def get_dynasties(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的最大记录数"),
    db: SQLiteManager = Depends(get_db)
):
    """获取所有朝代列表"""
    try:
        sql = """
            SELECT 
                d.*,
                (SELECT COUNT(*) FROM emperors WHERE dynasty_id = d.dynasty_id) as emperor_count
            FROM dynasties d
            ORDER BY start_year
            LIMIT ? OFFSET ?
        """
        rows = db.fetch_all(sql, (limit, skip))
        
        dynasties = []
        for row in rows:
            dynasties.append({
                "dynasty_id": row[0],
                "name": row[1],
                "start_year": row[2],
                "end_year": row[3],
                "capital": row[4],
                "founder": row[5],
                "description": row[6],
                "data_source": row[7],
                "emperor_count": row[10] if len(row) > 10 else 0
            })
        
        return dynasties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取朝代列表失败: {str(e)}")


@router.get("/{dynasty_id}", response_model=DynastyDetail)
async def get_dynasty(
    dynasty_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """获取朝代详情"""
    try:
        sql = """
            SELECT 
                d.*,
                (SELECT COUNT(*) FROM emperors WHERE dynasty_id = d.dynasty_id) as emperor_count
            FROM dynasties d
            WHERE d.dynasty_id = ?
        """
        row = db.fetch_one(sql, (dynasty_id,))
        
        if not row:
            raise HTTPException(status_code=404, detail=f"朝代不存在: {dynasty_id}")
        
        return {
            "dynasty_id": row[0],
            "name": row[1],
            "start_year": row[2],
            "end_year": row[3],
            "capital": row[4],
            "founder": row[5],
            "description": row[6],
            "data_source": row[7],
            "created_at": row[8],
            "updated_at": row[9],
            "emperor_count": row[10] if len(row) > 10 else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取朝代详情失败: {str(e)}")
