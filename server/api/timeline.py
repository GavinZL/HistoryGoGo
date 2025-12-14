"""
时间轴API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from collections import defaultdict
from server.schemas.timeline import TimelineResponse, TimelineItem, TimelineEvent, TimelineEmperor
from server.database.dependencies import get_db
from server.database.sqlite_manager import SQLiteManager

router = APIRouter()


@router.get("/{dynasty_id}", response_model=TimelineResponse)
async def get_timeline(
    dynasty_id: str,
    db: SQLiteManager = Depends(get_db)
):
    """获取指定朝代的时间轴数据"""
    try:
        # 获取朝代信息
        dynasty_sql = "SELECT dynasty_id, name, start_year, end_year FROM dynasties WHERE dynasty_id = ?"
        dynasty_row = db.fetch_one(dynasty_sql, (dynasty_id,))
        
        if not dynasty_row:
            raise HTTPException(status_code=404, detail=f"朝代不存在: {dynasty_id}")
        
        dynasty_name = dynasty_row[1]
        start_year = dynasty_row[2]
        end_year = dynasty_row[3]
        
        # 获取该朝代的所有事件
        events_sql = """
            SELECT event_id, title, event_type, start_date, location
            FROM events
            WHERE dynasty_id = ?
            ORDER BY start_date
        """
        event_rows = db.fetch_all(events_sql, (dynasty_id,))
        
        # 获取该朝代的所有皇帝
        emperors_sql = """
            SELECT emperor_id, name, temple_name, reign_start, reign_end
            FROM emperors
            WHERE dynasty_id = ?
            ORDER BY dynasty_order
        """
        emperor_rows = db.fetch_all(emperors_sql, (dynasty_id,))
        
        # 按年份组织时间轴数据
        timeline_dict: Dict[int, TimelineItem] = defaultdict(lambda: {
            "year": 0,
            "events": [],
            "emperor": None
        })
        
        # 添加事件到时间轴
        for event in event_rows:
            if event[3]:  # start_date
                try:
                    year = int(event[3][:4]) if isinstance(event[3], str) else event[3].year
                    timeline_dict[year]["year"] = year
                    timeline_dict[year]["events"].append({
                        "event_id": event[0],
                        "title": event[1],
                        "event_type": event[2],
                        "location": event[4]
                    })
                except (ValueError, AttributeError):
                    continue
        
        # 添加皇帝到时间轴（每年显示在位皇帝）
        for emperor in emperor_rows:
            if emperor[3] and emperor[4]:  # reign_start, reign_end
                try:
                    start = int(emperor[3][:4]) if isinstance(emperor[3], str) else emperor[3].year
                    end = int(emperor[4][:4]) if isinstance(emperor[4], str) else emperor[4].year
                    
                    for year in range(start, end + 1):
                        if year not in timeline_dict:
                            timeline_dict[year] = {
                                "year": year,
                                "events": [],
                                "emperor": None
                            }
                        
                        if timeline_dict[year]["emperor"] is None:
                            timeline_dict[year]["emperor"] = {
                                "emperor_id": emperor[0],
                                "name": emperor[1],
                                "temple_name": emperor[2],
                                "reign_start": emperor[3],
                                "reign_end": emperor[4]
                            }
                except (ValueError, AttributeError):
                    continue
        
        # 排序并转换为列表
        timeline = sorted(timeline_dict.values(), key=lambda x: x["year"])
        
        return {
            "dynasty_id": dynasty_id,
            "dynasty_name": dynasty_name,
            "start_year": start_year,
            "end_year": end_year,
            "timeline": timeline,
            "total_events": len(event_rows) if event_rows else 0,
            "total_emperors": len(emperor_rows) if emperor_rows else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间轴数据失败: {str(e)}")
