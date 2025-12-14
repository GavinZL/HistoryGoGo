"""
皇帝API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from server.schemas.emperor import EmperorResponse, EmperorSummary, EmperorDetail
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


@router.get("/", response_model=List[EmperorSummary])
async def get_emperors(
    dynasty_id: str = Query(None, description="按朝代筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: SQLiteManager = Depends(get_db)
):
    """获取皇帝列表"""
    try:
        if dynasty_id:
            sql = """
                SELECT emperor_id, name, temple_name, reign_title, 
                       reign_start, reign_end, reign_duration, dynasty_order, portrait_url
                FROM emperors
                WHERE dynasty_id = ?
                ORDER BY dynasty_order
                LIMIT ? OFFSET ?
            """
            rows = db.fetch_all(sql, (dynasty_id, limit, skip))
        else:
            sql = """
                SELECT emperor_id, name, temple_name, reign_title,
                       reign_start, reign_end, reign_duration, dynasty_order, portrait_url
                FROM emperors
                ORDER BY reign_start
                LIMIT ? OFFSET ?
            """
            rows = db.fetch_all(sql, (limit, skip))
        
        emperors = []
        for row in rows:
            emperors.append({
                "emperor_id": row[0],
                "name": row[1],
                "temple_name": row[2],
                "reign_title": row[3],
                "reign_start": row[4],
                "reign_end": row[5],
                "reign_duration": row[6],
                "dynasty_order": row[7],
                "portrait_url": row[8]
            })
        
        return emperors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取皇帝列表失败: {str(e)}")


@router.get("/{emperor_id}", response_model=EmperorDetail)
async def get_emperor(
    emperor_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """获取皇帝详情"""
    try:
        sql = """
            SELECT e.*,
                   (SELECT COUNT(*) FROM events WHERE emperor_id = e.emperor_id) as event_count,
                   (SELECT COUNT(*) FROM persons WHERE related_emperors LIKE '%' || e.emperor_id || '%') as person_count
            FROM emperors e
            WHERE e.emperor_id = ?
        """
        row = db.fetch_one(sql, (emperor_id,))
        
        if not row:
            raise HTTPException(status_code=404, detail=f"皇帝不存在: {emperor_id}")
        
        return {
            "emperor_id": row[0],
            "dynasty_id": row[1],
            "name": row[2],
            "temple_name": row[3],
            "reign_title": row[4],
            "birth_date": row[5],
            "death_date": row[6],
            "reign_start": row[7],
            "reign_end": row[8],
            "reign_duration": row[9],
            "dynasty_order": row[10],
            "biography": row[11],
            "achievements": row[12],
            "portrait_url": row[13],
            "data_source": row[14],
            "event_count": row[17] if len(row) > 17 else 0,
            "person_count": row[18] if len(row) > 18 else 0,
            "created_at": row[15] if len(row) > 15 else None,
            "updated_at": row[16] if len(row) > 16 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取皇帝详情失败: {str(e)}")
