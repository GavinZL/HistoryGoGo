"""
事件API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from server.schemas.event import EventSummary, EventDetail
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


@router.get("/", response_model=List[EventSummary])
async def get_events(
    dynasty_id: Optional[str] = Query(None, description="按朝代筛选"),
    emperor_id: Optional[str] = Query(None, description="按皇帝筛选"),
    event_type: Optional[str] = Query(None, description="按事件类型筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: SQLiteManager = Depends(get_db)
):
    """获取事件列表"""
    try:
        # 构建SQL查询
        sql = """
            SELECT event_id, title, event_type, start_date, end_date, location, dynasty_id, emperor_id
            FROM events
            WHERE 1=1
        """
        params = []
        
        if dynasty_id:
            sql += " AND dynasty_id = ?"
            params.append(dynasty_id)
        
        if emperor_id:
            sql += " AND emperor_id = ?"
            params.append(emperor_id)
        
        if event_type:
            sql += " AND event_type = ?"
            params.append(event_type)
        
        sql += " ORDER BY start_date LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        rows = db.fetch_all(sql, tuple(params))
        
        events = []
        for row in rows:
            events.append({
                "event_id": row[0],
                "title": row[1],
                "event_type": row[2],
                "start_date": row[3],
                "end_date": row[4],
                "location": row[5],
                "dynasty_id": row[6],
                "emperor_id": row[7]
            })
        
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取事件列表失败: {str(e)}")


@router.get("/{event_id}", response_model=EventDetail)
async def get_event(
    event_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """获取事件详情"""
    try:
        sql = """
            SELECT e.*,
                   (SELECT COUNT(*) FROM event_persons WHERE event_id = e.event_id) as person_count
            FROM events e
            WHERE e.event_id = ?
        """
        row = db.fetch_one(sql, (event_id,))
        
        if not row:
            raise HTTPException(status_code=404, detail=f"事件不存在: {event_id}")
        
        # 获取相关人物ID列表
        related_persons_sql = """
            SELECT person_id FROM event_persons WHERE event_id = ?
        """
        person_rows = db.fetch_all(related_persons_sql, (event_id,))
        related_persons = [p[0] for p in person_rows] if person_rows else []
        
        return {
            "event_id": row[0],
            "dynasty_id": row[1],
            "emperor_id": row[2],
            "title": row[3],
            "event_type": row[4],
            "start_date": row[5],
            "end_date": row[6],
            "location": row[7],
            "description": row[8],
            "participants": row[9],
            "casualties": row[10],
            "result": row[11],
            "significance": row[12],
            "data_source": row[13],
            "related_persons": related_persons,
            "person_count": row[16] if len(row) > 16 else 0,
            "created_at": row[14] if len(row) > 14 else None,
            "updated_at": row[15] if len(row) > 15 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取事件详情失败: {str(e)}")
