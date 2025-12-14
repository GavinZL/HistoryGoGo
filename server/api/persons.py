"""
人物API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from server.schemas.person import PersonSummary, PersonDetail
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


@router.get("/", response_model=List[PersonSummary])
async def get_persons(
    person_type: Optional[str] = Query(None, description="按人物类型筛选"),
    dynasty_id: Optional[str] = Query(None, description="按朝代筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: SQLiteManager = Depends(get_db)
):
    """获取人物列表"""
    try:
        # 构建SQL查询
        sql = """
            SELECT person_id, name, person_type, alias, birth_date, death_date, dynasty_id
            FROM persons
            WHERE 1=1
        """
        params = []
        
        if person_type:
            sql += " AND person_type = ?"
            params.append(person_type)
        
        if dynasty_id:
            sql += " AND dynasty_id = ?"
            params.append(dynasty_id)
        
        sql += " ORDER BY birth_date LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        rows = db.fetch_all(sql, tuple(params))
        
        persons = []
        for row in rows:
            persons.append({
                "person_id": row[0],
                "name": row[1],
                "person_type": row[2],
                "alias": row[3],
                "birth_date": row[4],
                "death_date": row[5],
                "dynasty_id": row[6]
            })
        
        return persons
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人物列表失败: {str(e)}")


@router.get("/{person_id}", response_model=PersonDetail)
async def get_person(
    person_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """获取人物详情"""
    try:
        sql = """
            SELECT p.*,
                   (SELECT COUNT(*) FROM event_persons WHERE person_id = p.person_id) as event_count,
                   (SELECT COUNT(*) FROM works WHERE author_id = p.person_id) as work_count
            FROM persons p
            WHERE p.person_id = ?
        """
        row = db.fetch_one(sql, (person_id,))
        
        if not row:
            raise HTTPException(status_code=404, detail=f"人物不存在: {person_id}")
        
        # 获取相关皇帝ID列表
        related_emperors = []
        if row[11]:  # related_emperors字段
            related_emperors = row[11].split(',') if ',' in row[11] else [row[11]]
        
        # 获取作品列表
        works_sql = "SELECT title FROM works WHERE author_id = ?"
        work_rows = db.fetch_all(works_sql, (person_id,))
        works = [w[0] for w in work_rows] if work_rows else []
        
        return {
            "person_id": row[0],
            "dynasty_id": row[1],
            "name": row[2],
            "person_type": row[3],
            "alias": row[4],
            "birth_date": row[5],
            "death_date": row[6],
            "position": row[7],
            "biography": row[8],
            "achievements": row[9],
            "data_source": row[10],
            "related_emperors": related_emperors,
            "style": row[12] if len(row) > 12 else None,
            "works": works,
            "event_count": row[15] if len(row) > 15 else 0,
            "work_count": row[16] if len(row) > 16 else 0,
            "created_at": row[13] if len(row) > 13 else None,
            "updated_at": row[14] if len(row) > 14 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人物详情失败: {str(e)}")
