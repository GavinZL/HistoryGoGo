"""
关系图谱API路由
利用Neo4j图数据库提供人物关系查询功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from server.database.neo4j_manager import get_neo4j_manager, Neo4jManager

router = APIRouter()


@router.get("/person/{person_id}")
async def get_person_relations(
    person_id: str,
    depth: int = Query(2, ge=1, le=3, description="关系深度（1-3层）"),
    relation_types: Optional[str] = Query(None, description="关系类型，逗号分隔"),
    max_nodes: int = Query(50, ge=10, le=200, description="最大节点数")
):
    """
    获取人物关系图谱
    
    返回以指定人物为中心的关系网络，包括：
    - 节点：人物、皇帝、事件
    - 边：关系类型和属性
    
    参数：
    - depth: 关系深度（默认2层，最多3层）
    - relation_types: 关系类型过滤，如 "FRIEND,TEACHER_STUDENT"
    - max_nodes: 最大节点数限制（避免返回数据过大）
    """
    try:
        neo4j_mgr = get_neo4j_manager()
        
        if not neo4j_mgr or not neo4j_mgr.test_connection():
            # Neo4j未连接，返回提示信息
            return {
                "person_id": person_id,
                "nodes": [],
                "edges": [],
                "message": "Neo4j图数据库未连接或未启动，关系图谱功能不可用"
            }
        
        # 解析关系类型
        relation_type_list = None
        if relation_types:
            relation_type_list = [rt.strip() for rt in relation_types.split(",")]
        
        # 查询关系图谱
        result = neo4j_mgr.get_person_relations(
            person_id=person_id,
            max_depth=depth,
            relation_types=relation_type_list
        )
        
        # 限制节点数量
        nodes = result.get("nodes", [])
        edges = result.get("edges", [])
        
        if len(nodes) > max_nodes:
            # 简化：只保留最重要的节点（可以优化为按重要性排序）
            nodes = nodes[:max_nodes]
            node_ids = {node["id"] for node in nodes}
            edges = [edge for edge in edges 
                    if edge["source"] in node_ids and edge["target"] in node_ids]
        
        return {
            "person_id": person_id,
            "depth": depth,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人物关系图谱失败: {str(e)}")


@router.get("/path")
async def find_relation_path(
    from_person_id: str = Query(..., description="起始人物ID"),
    to_person_id: str = Query(..., description="目标人物ID"),
    max_depth: int = Query(5, ge=1, le=10, description="最大搜索深度")
):
    """
    查找两个人物之间的关系路径
    
    返回最短关系路径，展示两人如何通过关系连接。
    
    示例：
    - 从郑和到朱棣：郑和 -[SERVED_UNDER]-> 朱棣
    - 从A到B：A -[FRIEND]-> C -[TEACHER_STUDENT]-> B
    """
    try:
        neo4j_mgr = get_neo4j_manager()
        
        if not neo4j_mgr or not neo4j_mgr.test_connection():
            return {
                "from_person_id": from_person_id,
                "to_person_id": to_person_id,
                "found": False,
                "message": "Neo4j图数据库未连接或未启动"
            }
        
        # 查找最短路径
        result = neo4j_mgr.find_shortest_path(
            from_person_id=from_person_id,
            to_person_id=to_person_id,
            max_depth=max_depth
        )
        
        if result.get("found"):
            return {
                "from_person_id": from_person_id,
                "to_person_id": to_person_id,
                "found": True,
                "path": result["path"],
                "relations": result["relations"],
                "distance": result["distance"]
            }
        else:
            return {
                "from_person_id": from_person_id,
                "to_person_id": to_person_id,
                "found": False,
                "message": f"在{max_depth}层深度内未找到关系路径"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查找关系路径失败: {str(e)}")


@router.get("/event/{event_id}/participants")
async def get_event_participants(
    event_id: str
):
    """
    获取事件的所有参与者
    
    返回参与指定事件的所有人物，包括他们在事件中的角色。
    """
    try:
        neo4j_mgr = get_neo4j_manager()
        
        if not neo4j_mgr or not neo4j_mgr.test_connection():
            return {
                "event_id": event_id,
                "participants": [],
                "message": "Neo4j图数据库未连接或未启动"
            }
        
        participants = neo4j_mgr.get_event_participants(event_id)
        
        return {
            "event_id": event_id,
            "participants": participants,
            "total": len(participants)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取事件参与者失败: {str(e)}")


@router.get("/emperor/{emperor_id}/ministers")
async def get_emperor_ministers(
    emperor_id: str
):
    """
    获取皇帝的臣子
    
    返回侍奉指定皇帝的所有臣子，包括他们的职位。
    """
    try:
        neo4j_mgr = get_neo4j_manager()
        
        if not neo4j_mgr or not neo4j_mgr.test_connection():
            return {
                "emperor_id": emperor_id,
                "ministers": [],
                "message": "Neo4j图数据库未连接或未启动"
            }
        
        ministers = neo4j_mgr.get_emperor_ministers(emperor_id)
        
        return {
            "emperor_id": emperor_id,
            "ministers": ministers,
            "total": len(ministers)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取皇帝臣子失败: {str(e)}")


@router.get("/test")
async def test_neo4j_connection():
    """
    测试Neo4j连接状态
    
    用于检查Neo4j图数据库是否正常连接。
    """
    try:
        neo4j_mgr = get_neo4j_manager()
        
        if not neo4j_mgr:
            return {
                "connected": False,
                "message": "Neo4j管理器未初始化"
            }
        
        is_connected = neo4j_mgr.test_connection()
        
        return {
            "connected": is_connected,
            "message": "Neo4j连接正常" if is_connected else "Neo4j连接失败"
        }
        
    except Exception as e:
        return {
            "connected": False,
            "message": f"测试失败: {str(e)}"
        }
