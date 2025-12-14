"""
统计数据API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


@router.get("/overview")
async def get_overview_statistics(
    db: SQLiteManager = Depends(get_db)
):
    """
    获取整体统计数据概览
    
    返回：
    - 朝代数量
    - 皇帝数量
    - 事件数量
    - 人物数量
    - 作品数量
    """
    try:
        stats = {}
        
        # 统计朝代数量
        dynasty_count_sql = "SELECT COUNT(*) FROM dynasties"
        dynasty_count = db.fetch_one(dynasty_count_sql)
        stats["dynasty_count"] = dynasty_count[0] if dynasty_count else 0
        
        # 统计皇帝数量
        emperor_count_sql = "SELECT COUNT(*) FROM emperors"
        emperor_count = db.fetch_one(emperor_count_sql)
        stats["emperor_count"] = emperor_count[0] if emperor_count else 0
        
        # 统计事件数量
        event_count_sql = "SELECT COUNT(*) FROM events"
        event_count = db.fetch_one(event_count_sql)
        stats["event_count"] = event_count[0] if event_count else 0
        
        # 统计人物数量
        person_count_sql = "SELECT COUNT(*) FROM persons"
        person_count = db.fetch_one(person_count_sql)
        stats["person_count"] = person_count[0] if person_count else 0
        
        # 统计作品数量
        work_count_sql = "SELECT COUNT(*) FROM works"
        work_count = db.fetch_one(work_count_sql)
        stats["work_count"] = work_count[0] if work_count else 0
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/dynasty/{dynasty_id}")
async def get_dynasty_statistics(
    dynasty_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """
    获取指定朝代的统计数据
    
    返回：
    - 朝代基本信息
    - 皇帝数量和平均在位时长
    - 事件数量（按类型分类）
    - 人物数量（按类型分类）
    - 国祚（朝代持续时间）
    """
    try:
        # 获取朝代基本信息
        dynasty_sql = "SELECT dynasty_id, name, start_year, end_year FROM dynasties WHERE dynasty_id = ?"
        dynasty_row = db.fetch_one(dynasty_sql, (dynasty_id,))
        
        if not dynasty_row:
            raise HTTPException(status_code=404, detail=f"朝代不存在: {dynasty_id}")
        
        stats = {
            "dynasty_id": dynasty_row[0],
            "dynasty_name": dynasty_row[1],
            "start_year": dynasty_row[2],
            "end_year": dynasty_row[3],
            "duration_years": dynasty_row[3] - dynasty_row[2]
        }
        
        # 统计皇帝数量和平均在位时长
        emperor_stats_sql = """
            SELECT COUNT(*), AVG(reign_duration)
            FROM emperors
            WHERE dynasty_id = ?
        """
        emperor_stats = db.fetch_one(emperor_stats_sql, (dynasty_id,))
        stats["emperor_count"] = emperor_stats[0] if emperor_stats else 0
        stats["avg_reign_duration"] = round(emperor_stats[1], 1) if emperor_stats and emperor_stats[1] else 0
        
        # 统计事件数量（按类型）
        event_type_sql = """
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE dynasty_id = ?
            GROUP BY event_type
            ORDER BY count DESC
        """
        event_type_rows = db.fetch_all(event_type_sql, (dynasty_id,))
        stats["event_count_by_type"] = {}
        stats["total_events"] = 0
        if event_type_rows:
            for row in event_type_rows:
                stats["event_count_by_type"][row[0]] = row[1]
                stats["total_events"] += row[1]
        
        # 统计人物数量（按类型）
        person_type_sql = """
            SELECT person_type, COUNT(*) as count
            FROM persons
            WHERE dynasty_id = ?
            GROUP BY person_type
            ORDER BY count DESC
        """
        person_type_rows = db.fetch_all(person_type_sql, (dynasty_id,))
        stats["person_count_by_type"] = {}
        stats["total_persons"] = 0
        if person_type_rows:
            for row in person_type_rows:
                stats["person_count_by_type"][row[0]] = row[1]
                stats["total_persons"] += row[1]
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取朝代统计失败: {str(e)}")


@router.get("/emperor/{emperor_id}")
async def get_emperor_statistics(
    emperor_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """
    获取指定皇帝的统计数据
    
    返回：
    - 在位时长
    - 相关事件数量（按类型）
    - 相关人物数量（按类型）
    """
    try:
        # 获取皇帝基本信息
        emperor_sql = """
            SELECT emperor_id, name, temple_name, reign_start, reign_end, reign_duration
            FROM emperors
            WHERE emperor_id = ?
        """
        emperor_row = db.fetch_one(emperor_sql, (emperor_id,))
        
        if not emperor_row:
            raise HTTPException(status_code=404, detail=f"皇帝不存在: {emperor_id}")
        
        stats = {
            "emperor_id": emperor_row[0],
            "name": emperor_row[1],
            "temple_name": emperor_row[2],
            "reign_start": emperor_row[3],
            "reign_end": emperor_row[4],
            "reign_duration": emperor_row[5]
        }
        
        # 统计相关事件（按类型）
        event_type_sql = """
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE emperor_id = ?
            GROUP BY event_type
            ORDER BY count DESC
        """
        event_type_rows = db.fetch_all(event_type_sql, (emperor_id,))
        stats["event_count_by_type"] = {}
        stats["total_events"] = 0
        if event_type_rows:
            for row in event_type_rows:
                stats["event_count_by_type"][row[0]] = row[1]
                stats["total_events"] += row[1]
        
        # 获取事件列表（TOP 10）
        top_events_sql = """
            SELECT event_id, title, event_type, start_date
            FROM events
            WHERE emperor_id = ?
            ORDER BY start_date
            LIMIT 10
        """
        top_events_rows = db.fetch_all(top_events_sql, (emperor_id,))
        stats["major_events"] = []
        if top_events_rows:
            for row in top_events_rows:
                stats["major_events"].append({
                    "event_id": row[0],
                    "title": row[1],
                    "event_type": row[2],
                    "date": row[3]
                })
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取皇帝统计失败: {str(e)}")


@router.get("/trends/timeline")
async def get_timeline_trends(
    dynasty_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """
    获取时间线趋势数据
    
    返回每年的事件数量，用于可视化时间线趋势
    """
    try:
        # 获取朝代时间范围
        dynasty_sql = "SELECT start_year, end_year FROM dynasties WHERE dynasty_id = ?"
        dynasty_row = db.fetch_one(dynasty_sql, (dynasty_id,))
        
        if not dynasty_row:
            raise HTTPException(status_code=404, detail=f"朝代不存在: {dynasty_id}")
        
        start_year = dynasty_row[0]
        end_year = dynasty_row[1]
        
        # 统计每年的事件数量
        yearly_events_sql = """
            SELECT 
                CAST(SUBSTR(start_date, 1, 4) AS INTEGER) as year,
                COUNT(*) as count
            FROM events
            WHERE dynasty_id = ?
            AND start_date IS NOT NULL
            GROUP BY year
            ORDER BY year
        """
        yearly_rows = db.fetch_all(yearly_events_sql, (dynasty_id,))
        
        # 构建年份事件映射
        year_event_map = {}
        if yearly_rows:
            for row in yearly_rows:
                year_event_map[row[0]] = row[1]
        
        # 生成完整年份数据（填充0）
        timeline_data = []
        for year in range(start_year, end_year + 1):
            timeline_data.append({
                "year": year,
                "event_count": year_event_map.get(year, 0)
            })
        
        return {
            "dynasty_id": dynasty_id,
            "start_year": start_year,
            "end_year": end_year,
            "data": timeline_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间线趋势失败: {str(e)}")


@router.get("/rankings/emperors")
async def get_emperor_rankings(
    metric: str = "reign_duration",
    limit: int = 10,
    db: SQLiteManager = Depends(get_db)
):
    """
    获取皇帝排名
    
    支持的排名指标：
    - reign_duration: 在位时长
    - event_count: 相关事件数量
    """
    try:
        if metric == "reign_duration":
            sql = """
                SELECT emperor_id, name, temple_name, reign_duration, dynasty_id
                FROM emperors
                WHERE reign_duration IS NOT NULL
                ORDER BY reign_duration DESC
                LIMIT ?
            """
        elif metric == "event_count":
            sql = """
                SELECT e.emperor_id, e.name, e.temple_name, e.dynasty_id, COUNT(ev.event_id) as event_count
                FROM emperors e
                LEFT JOIN events ev ON e.emperor_id = ev.emperor_id
                GROUP BY e.emperor_id
                ORDER BY event_count DESC
                LIMIT ?
            """
        else:
            raise HTTPException(status_code=400, detail=f"不支持的排名指标: {metric}")
        
        rows = db.fetch_all(sql, (limit,))
        
        rankings = []
        if rows:
            for idx, row in enumerate(rows, 1):
                rankings.append({
                    "rank": idx,
                    "emperor_id": row[0],
                    "name": row[1],
                    "temple_name": row[2],
                    "value": row[3] if metric == "reign_duration" else row[4],
                    "dynasty_id": row[3] if metric == "reign_duration" else row[4]
                })
        
        return {
            "metric": metric,
            "limit": limit,
            "rankings": rankings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取皇帝排名失败: {str(e)}")
