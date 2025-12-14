"""
Neo4j数据库管理器
用于图数据库操作
"""
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Neo4jManager:
    """Neo4j数据库管理器"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """
        初始化Neo4j连接
        
        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info(f"Neo4j连接成功: {uri}")
        except Exception as e:
            logger.error(f"Neo4j连接失败: {str(e)}")
            self.driver = None
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭")
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行Cypher查询
        
        Args:
            query: Cypher查询语句
            parameters: 查询参数
            
        Returns:
            查询结果列表
        """
        if not self.driver:
            logger.warning("Neo4j未连接，返回空结果")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            return []
    
    def get_person_relations(
        self,
        person_id: str,
        max_depth: int = 2,
        relation_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        获取人物关系图谱
        
        Args:
            person_id: 人物ID
            max_depth: 关系深度（默认2层）
            relation_types: 关系类型过滤列表
            
        Returns:
            包含节点和边的图谱数据
        """
        if not self.driver:
            return {"nodes": [], "edges": []}
        
        # 构建关系类型过滤条件
        rel_filter = ""
        if relation_types:
            rel_filter = f":{':'.join(relation_types)}"
        
        # Cypher查询：获取person_id为中心的关系网络
        query = f"""
        MATCH path = (p:Person {{id: $person_id}})-[r{rel_filter}*1..{max_depth}]-(related)
        WHERE related:Person OR related:Emperor OR related:Event
        WITH nodes(path) as pathNodes, relationships(path) as pathRels
        UNWIND pathNodes as node
        WITH collect(DISTINCT node) as allNodes, pathRels
        UNWIND pathRels as rel
        WITH allNodes, collect(DISTINCT rel) as allRels
        RETURN 
            [n in allNodes | {{
                id: n.id,
                label: COALESCE(n.name, n.title),
                type: labels(n)[0],
                properties: properties(n)
            }}] as nodes,
            [r in allRels | {{
                source: startNode(r).id,
                target: endNode(r).id,
                relation_type: type(r),
                properties: properties(r)
            }}] as edges
        """
        
        try:
            result = self.execute_query(query, {"person_id": person_id})
            if result and len(result) > 0:
                return result[0]
            return {"nodes": [], "edges": []}
        except Exception as e:
            logger.error(f"获取人物关系失败: {str(e)}")
            return {"nodes": [], "edges": []}
    
    def find_shortest_path(
        self,
        from_person_id: str,
        to_person_id: str,
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """
        查找两个人物之间的最短关系路径
        
        Args:
            from_person_id: 起始人物ID
            to_person_id: 目标人物ID
            max_depth: 最大搜索深度
            
        Returns:
            最短路径数据
        """
        if not self.driver:
            return {"found": False, "path": []}
        
        query = """
        MATCH path = shortestPath(
            (p1:Person {id: $from_id})-[*1..%d]-(p2:Person {id: $to_id})
        )
        WHERE p1 <> p2
        RETURN 
            [n in nodes(path) | {
                id: n.id,
                name: n.name,
                type: labels(n)[0]
            }] as nodes,
            [r in relationships(path) | {
                type: type(r),
                properties: properties(r)
            }] as relations,
            length(path) as distance
        """ % max_depth
        
        try:
            result = self.execute_query(query, {
                "from_id": from_person_id,
                "to_id": to_person_id
            })
            
            if result and len(result) > 0:
                return {
                    "found": True,
                    "path": result[0]["nodes"],
                    "relations": result[0]["relations"],
                    "distance": result[0]["distance"]
                }
            return {"found": False, "path": []}
        except Exception as e:
            logger.error(f"查找最短路径失败: {str(e)}")
            return {"found": False, "path": []}
    
    def get_event_participants(self, event_id: str) -> List[Dict[str, Any]]:
        """
        获取事件的所有参与者
        
        Args:
            event_id: 事件ID
            
        Returns:
            参与者列表
        """
        if not self.driver:
            return []
        
        query = """
        MATCH (e:Event {id: $event_id})<-[r:PARTICIPATED_IN]-(p:Person)
        RETURN p.id as person_id, p.name as name, p.person_type as type, r.role as role
        """
        
        try:
            return self.execute_query(query, {"event_id": event_id})
        except Exception as e:
            logger.error(f"获取事件参与者失败: {str(e)}")
            return []
    
    def get_emperor_ministers(self, emperor_id: str) -> List[Dict[str, Any]]:
        """
        获取皇帝的臣子
        
        Args:
            emperor_id: 皇帝ID
            
        Returns:
            臣子列表
        """
        if not self.driver:
            return []
        
        query = """
        MATCH (p:Person)-[r:SERVED_UNDER]->(e:Emperor {id: $emperor_id})
        RETURN p.id as person_id, p.name as name, p.person_type as type, r.position as position
        ORDER BY p.name
        """
        
        try:
            return self.execute_query(query, {"emperor_id": emperor_id})
        except Exception as e:
            logger.error(f"获取皇帝臣子失败: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否成功
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False


# 全局Neo4j管理器实例（可选）
_neo4j_manager: Optional[Neo4jManager] = None


def get_neo4j_manager() -> Optional[Neo4jManager]:
    """获取Neo4j管理器实例"""
    global _neo4j_manager
    if _neo4j_manager is None:
        try:
            _neo4j_manager = Neo4jManager()
        except Exception as e:
            logger.error(f"初始化Neo4j管理器失败: {str(e)}")
    return _neo4j_manager


def close_neo4j():
    """关闭Neo4j连接"""
    global _neo4j_manager
    if _neo4j_manager:
        _neo4j_manager.close()
        _neo4j_manager = None
