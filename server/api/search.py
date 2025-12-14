"""
全局搜索API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from server.schemas.common import SuccessResponse
from server.schemas.emperor import EmperorSummary
from server.schemas.event import EventSummary
from server.schemas.person import PersonSummary
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


class SearchResult:
    """搜索结果"""
    def __init__(self):
        self.emperors: List[EmperorSummary] = []
        self.events: List[EventSummary] = []
        self.persons: List[PersonSummary] = []
        self.total: int = 0


@router.get("/", response_model=dict)
async def global_search(
    q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    search_type: Optional[str] = Query(None, description="搜索类型: emperor/event/person/all"),
    dynasty_id: Optional[str] = Query(None, description="限定朝代"),
    limit: int = Query(20, ge=1, le=100, description="每个类型的结果数量限制"),
    db: SQLiteManager = Depends(get_db)
):
    """
    全局搜索功能
    
    支持搜索：
    - 皇帝：姓名、庙号、谥号、年号
    - 事件：标题、描述
    - 人物：姓名、别名、职位
    """
    try:
        result = {
            "keyword": q,
            "emperors": [],
            "events": [],
            "persons": [],
            "total": 0
        }
        
        # 搜索皇帝
        if search_type is None or search_type == "all" or search_type == "emperor":
            emperor_sql = """
                SELECT emperor_id, name, temple_name, reign_title, reign_start, reign_end, dynasty_id
                FROM emperors
                WHERE (name LIKE ? OR temple_name LIKE ? OR reign_title LIKE ?)
            """
            params = [f"%{q}%", f"%{q}%", f"%{q}%"]
            
            if dynasty_id:
                emperor_sql += " AND dynasty_id = ?"
                params.append(dynasty_id)
            
            emperor_sql += " LIMIT ?"
            params.append(limit)
            
            emperor_rows = db.fetch_all(emperor_sql, tuple(params))
            
            if emperor_rows:
                for row in emperor_rows:
                    result["emperors"].append({
                        "emperor_id": row[0],
                        "name": row[1],
                        "temple_name": row[2],
                        "reign_title": row[3],
                        "reign_start": row[4],
                        "reign_end": row[5],
                        "dynasty_id": row[6]
                    })
        
        # 搜索事件
        if search_type is None or search_type == "all" or search_type == "event":
            event_sql = """
                SELECT event_id, title, event_type, start_date, end_date, location, dynasty_id, emperor_id
                FROM events
                WHERE (title LIKE ? OR description LIKE ?)
            """
            params = [f"%{q}%", f"%{q}%"]
            
            if dynasty_id:
                event_sql += " AND dynasty_id = ?"
                params.append(dynasty_id)
            
            event_sql += " ORDER BY start_date LIMIT ?"
            params.append(limit)
            
            event_rows = db.fetch_all(event_sql, tuple(params))
            
            if event_rows:
                for row in event_rows:
                    result["events"].append({
                        "event_id": row[0],
                        "title": row[1],
                        "event_type": row[2],
                        "start_date": row[3],
                        "end_date": row[4],
                        "location": row[5],
                        "dynasty_id": row[6],
                        "emperor_id": row[7]
                    })
        
        # 搜索人物
        if search_type is None or search_type == "all" or search_type == "person":
            person_sql = """
                SELECT person_id, name, person_type, alias, birth_date, death_date, dynasty_id
                FROM persons
                WHERE (name LIKE ? OR alias LIKE ? OR position LIKE ?)
            """
            params = [f"%{q}%", f"%{q}%", f"%{q}%"]
            
            if dynasty_id:
                person_sql += " AND dynasty_id = ?"
                params.append(dynasty_id)
            
            person_sql += " LIMIT ?"
            params.append(limit)
            
            person_rows = db.fetch_all(person_sql, tuple(params))
            
            if person_rows:
                for row in person_rows:
                    result["persons"].append({
                        "person_id": row[0],
                        "name": row[1],
                        "person_type": row[2],
                        "alias": row[3],
                        "birth_date": row[4],
                        "death_date": row[5],
                        "dynasty_id": row[6]
                    })
        
        # 计算总数
        result["total"] = len(result["emperors"]) + len(result["events"]) + len(result["persons"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/suggest")
async def search_suggest(
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词前缀"),
    limit: int = Query(5, ge=1, le=20, description="建议数量"),
    db: SQLiteManager = Depends(get_db)
):
    """
    搜索建议
    
    根据输入前缀返回搜索建议
    """
    try:
        suggestions = []
        
        # 从皇帝表获取建议
        emperor_sql = """
            SELECT DISTINCT name FROM emperors
            WHERE name LIKE ?
            LIMIT ?
        """
        emperor_rows = db.fetch_all(emperor_sql, (f"{q}%", limit))
        suggestions.extend([{"text": row[0], "type": "emperor"} for row in emperor_rows] if emperor_rows else [])
        
        # 从人物表获取建议
        person_sql = """
            SELECT DISTINCT name FROM persons
            WHERE name LIKE ?
            LIMIT ?
        """
        person_rows = db.fetch_all(person_sql, (f"{q}%", limit))
        suggestions.extend([{"text": row[0], "type": "person"} for row in person_rows] if person_rows else [])
        
        # 去重并限制数量
        unique_suggestions = []
        seen = set()
        for s in suggestions:
            if s["text"] not in seen:
                unique_suggestions.append(s)
                seen.add(s["text"])
                if len(unique_suggestions) >= limit:
                    break
        
        return {
            "keyword": q,
            "suggestions": unique_suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取搜索建议失败: {str(e)}")
