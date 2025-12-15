"""
Neo4j持久化管道
将爬取的数据保存到Neo4j图数据库，构建知识图谱
"""

from typing import Any
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crawler.models.entities import Emperor, Event, Person


class Neo4jPipeline:
    """Neo4j图数据库持久化管道"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """
        初始化Neo4j连接
        
        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.stats = {
            'nodes_created': 0,
            'relationships_created': 0,
            'errors': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        从Scrapy配置中读取Neo4j连接参数
        
        Args:
            crawler: Scrapy Crawler对象
        
        Returns:
            Neo4jPipeline实例
        """
        return cls(
            uri=crawler.settings.get('NEO4J_URI', 'bolt://localhost:7687'),
            user=crawler.settings.get('NEO4J_USER', 'neo4j'),
            password=crawler.settings.get('NEO4J_PASSWORD', 'password')
        )
    
    def open_spider(self, spider):
        """爬虫启动时连接Neo4j"""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            spider.logger.info(f"已连接到Neo4j: {self.uri}")
        except ImportError:
            spider.logger.warning("未安装neo4j驱动，跳过Neo4j持久化")
            self.driver = None
        except Exception as e:
            spider.logger.error(f"Neo4j连接失败: {str(e)}")
            self.driver = None
    
    def close_spider(self, spider):
        """爬虫关闭时输出统计并关闭连接"""
        if self.driver:
            spider.logger.info(
                f"Neo4j持久化统计: "
                f"节点={self.stats['nodes_created']}, "
                f"关系={self.stats['relationships_created']}, "
                f"错误={self.stats['errors']}"
            )
            self.driver.close()
    
    def process_item(self, item: Any, spider):
        """处理数据项"""
        if not self.driver:
            return item
        
        try:
            with self.driver.session() as session:
                if isinstance(item, Emperor):
                    self._save_emperor(session, item, spider)
                elif isinstance(item, Event):
                    self._save_event(session, item, spider)
                elif isinstance(item, Person):
                    self._save_person(session, item, spider)
            
            return item
        
        except Exception as e:
            self.stats['errors'] += 1
            spider.logger.error(f"Neo4j保存失败: {str(e)}")
            return item
    
    def _save_emperor(self, session, emperor: Emperor, spider):
        """保存皇帝节点及关系"""
        # 数据验证：检查必填字段
        if not emperor.emperor_id:
            spider.logger.error(f"❌ Neo4j保存失败: 皇帝ID为空")
            raise ValueError("Emperor ID cannot be empty")
        
        if not emperor.name:
            spider.logger.error(f"❌ Neo4j保存失败: 皇帝姓名为空 (ID: {emperor.emperor_id})")
            raise ValueError("Emperor name cannot be empty")
        
        if not emperor.dynasty_id:
            spider.logger.error(f"❌ Neo4j保存失败: 朝代ID为空 (皇帝: {emperor.name})")
            raise ValueError("Dynasty ID cannot be empty")
        
        if emperor.dynasty_order is None or emperor.dynasty_order < 1:
            spider.logger.error(f"❌ Neo4j保存失败: 朝代顺序无效 (皇帝: {emperor.name}, order: {emperor.dynasty_order})")
            raise ValueError("Invalid dynasty order")
        
        spider.logger.debug(f"💾 准备保存皇帝到Neo4j: {emperor.name} (ID: {emperor.emperor_id})")
        
        # 创建皇帝节点
        query = """
        MERGE (e:Emperor {id: $emperor_id})
        SET e.name = $name,
            e.temple_name = $temple_name,
            e.dynasty_order = $dynasty_order
        WITH e
        MERGE (d:Dynasty {id: $dynasty_id})
        MERGE (e)-[:BELONGS_TO]->(d)
        MERGE (d)-[:RULED_BY {
            reign_start: $reign_start,
            reign_end: $reign_end
        }]->(e)
        RETURN e
        """
        
        params = {
            'emperor_id': emperor.emperor_id,
            'name': emperor.name,
            'temple_name': emperor.temple_name or '',
            'dynasty_order': emperor.dynasty_order,
            'dynasty_id': emperor.dynasty_id,
            'reign_start': emperor.reign_start.isoformat() if emperor.reign_start else None,
            'reign_end': emperor.reign_end.isoformat() if emperor.reign_end else None
        }
        
        try:
            result = session.run(query, params)
            if result.single():
                self.stats['nodes_created'] += 1
                self.stats['relationships_created'] += 2
                spider.logger.info(f"✅ Neo4j保存成功: 皇帝 {emperor.name}")
        except Exception as e:
            spider.logger.error(f"❌ Neo4j保存皇帝失败: {emperor.name}")
            spider.logger.error(f"   错误详情: {str(e)}")
            spider.logger.error(f"   参数: emperor_id={params['emperor_id']}, name={params['name']}, dynasty_id={params['dynasty_id']}")
            raise
        
        # 创建皇位继承关系（如果有前一位皇帝）
        if emperor.dynasty_order > 1:
            self._create_succession_relation(session, emperor, spider)
    
    def _create_succession_relation(self, session, emperor: Emperor, spider):
        """创建皇位继承关系"""
        query = """
        MATCH (prev:Emperor {dynasty_order: $prev_order})
        WHERE prev.id STARTS WITH 'ming_emperor'
        MATCH (curr:Emperor {id: $curr_id})
        MERGE (prev)-[:SUCCEEDED_BY]->(curr)
        RETURN prev, curr
        """
        
        params = {
            'prev_order': emperor.dynasty_order - 1,
            'curr_id': emperor.emperor_id
        }
        
        result = session.run(query, params)
        if result.single():
            self.stats['relationships_created'] += 1
    
    def _save_event(self, session, event: Event, spider):
        """保存事件节点及关系"""
        # 数据验证：检查必填字段
        if not event.event_id:
            spider.logger.error(f"❌ Neo4j保存失败: 事件ID为空")
            raise ValueError("Event ID cannot be empty")
        
        if not event.title:
            spider.logger.error(f"❌ Neo4j保存失败: 事件标题为空 (ID: {event.event_id})")
            raise ValueError("Event title cannot be empty")
        
        if not event.dynasty_id:
            spider.logger.error(f"❌ Neo4j保存失败: 朝代ID为空 (事件: {event.title})")
            raise ValueError("Dynasty ID cannot be empty")
        
        spider.logger.debug(f"💾 准备保存事件到Neo4j: {event.title} (ID: {event.event_id})")
        
        # 创建事件节点
        query = """
        MERGE (ev:Event {id: $event_id})
        SET ev.title = $title,
            ev.event_type = $event_type,
            ev.start_date = $start_date
        WITH ev
        MERGE (d:Dynasty {id: $dynasty_id})
        MERGE (ev)-[:BELONGS_TO]->(d)
        """
        
        params = {
            'event_id': event.event_id,
            'title': event.title or '',
            'event_type': event.event_type.value if event.event_type else None,
            'start_date': event.start_date.isoformat() if event.start_date else None,
            'dynasty_id': event.dynasty_id
        }
        
        # 如果有关联皇帝，添加关系
        if event.emperor_id:
            query += """
            WITH ev
            MERGE (e:Emperor {id: $emperor_id})
            MERGE (ev)-[:OCCURRED_DURING]->(e)
            """
            params['emperor_id'] = event.emperor_id
        
        query += " RETURN ev"
        
        try:
            result = session.run(query, params)
            if result.single():
                self.stats['nodes_created'] += 1
                self.stats['relationships_created'] += 1  # BELONGS_TO
                if event.emperor_id:
                    self.stats['relationships_created'] += 1  # OCCURRED_DURING
                spider.logger.info(f"✅ Neo4j保存成功: 事件 {event.title}")
        except Exception as e:
            spider.logger.error(f"❌ Neo4j保存事件失败: {event.title}")
            spider.logger.error(f"   错误详情: {str(e)}")
            spider.logger.error(f"   参数: event_id={params['event_id']}, title={params['title']}, dynasty_id={params['dynasty_id']}")
            raise
    
    def _save_person(self, session, person: Person, spider):
        """保存人物节点及关系"""
        # 数据验证：检查必填字段
        if not person.person_id:
            spider.logger.error(f"❌ Neo4j保存失败: 人物ID为空")
            raise ValueError("Person ID cannot be empty")
        
        if not person.name:
            spider.logger.error(f"❌ Neo4j保存失败: 人物姓名为空 (ID: {person.person_id})")
            raise ValueError("Person name cannot be empty")
        
        if not person.dynasty_id:
            spider.logger.error(f"❌ Neo4j保存失败: 朝代ID为空 (人物: {person.name})")
            raise ValueError("Dynasty ID cannot be empty")
        
        spider.logger.debug(f"💾 准备保存人物到Neo4j: {person.name} (ID: {person.person_id})")
        
        # 创建人物节点
        query = """
        MERGE (p:Person {id: $person_id})
        SET p.name = $name,
            p.person_type = $person_type
        WITH p
        MERGE (d:Dynasty {id: $dynasty_id})
        MERGE (p)-[:BELONGS_TO]->(d)
        """
        
        params = {
            'person_id': person.person_id,
            'name': person.name or '',
            'person_type': person.person_type.value if person.person_type else None,
            'dynasty_id': person.dynasty_id
        }
        
        # 如果有关联皇帝，添加侍奉关系
        if person.related_emperors:
            query += """
            WITH p
            UNWIND $emperor_ids AS emperor_id
            MERGE (e:Emperor {id: emperor_id})
            MERGE (p)-[:SERVED_UNDER {position: $position}]->(e)
            """
            params['emperor_ids'] = person.related_emperors
            params['position'] = person.position or ''
        
        query += " RETURN p"
        
        try:
            result = session.run(query, params)
            if result.single():
                self.stats['nodes_created'] += 1
                self.stats['relationships_created'] += 1  # BELONGS_TO
                if person.related_emperors:
                    self.stats['relationships_created'] += len(person.related_emperors)  # SERVED_UNDER
                spider.logger.info(f"✅ Neo4j保存成功: 人物 {person.name}")
        except Exception as e:
            spider.logger.error(f"❌ Neo4j保存人物失败: {person.name}")
            spider.logger.error(f"   错误详情: {str(e)}")
            spider.logger.error(f"   参数: person_id={params['person_id']}, name={params['name']}, dynasty_id={params['dynasty_id']}")
            raise


# Neo4j管理器（用于初始化和维护）
class Neo4jManager:
    """Neo4j数据库管理器"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    def connect(self):
        """连接Neo4j数据库"""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            print(f"✅ 已连接到Neo4j: {self.uri}")
        except ImportError:
            print("❌ 未安装neo4j驱动，请运行: pip install neo4j")
            raise
        except Exception as e:
            print(f"❌ Neo4j连接失败: {str(e)}")
            raise
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    def initialize_database(self):
        """初始化数据库（创建约束和索引）"""
        cypher_file = Path(__file__).parent.parent.parent / 'server' / 'database' / 'init_neo4j.cypher'
        
        if not cypher_file.exists():
            raise FileNotFoundError(f"Cypher初始化文件不存在: {cypher_file}")
        
        # 读取Cypher脚本
        with open(cypher_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤注释行并合并查询
        queries = []
        current_query = []
        
        for line in lines:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('//'):
                continue
            
            current_query.append(line)
            
            # 如果行以分号结尾，表示一个查询结束
            if line.endswith(';'):
                query = ' '.join(current_query)
                queries.append(query)
                current_query = []
        
        # 执行所有查询
        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                    print(f"✅ 执行成功")
                except Exception as e:
                    print(f"⚠️  查询执行失败: {str(e)}")
        
        print("✅ Neo4j数据库初始化完成")
    
    def get_stats(self):
        """获取数据库统计信息"""
        with self.driver.session() as session:
            # 统计节点数量
            result = session.run("MATCH (n) RETURN labels(n) as label, count(n) as count")
            
            print("\n" + "=" * 50)
            print("Neo4j数据库统计")
            print("=" * 50)
            
            total_nodes = 0
            for record in result:
                label = record['label'][0] if record['label'] else 'Unknown'
                count = record['count']
                total_nodes += count
                print(f"  {label:20s} {count:>8,d} 个节点")
            
            print(f"  {'总计':20s} {total_nodes:>8,d} 个节点")
            
            # 统计关系数量
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
            
            print("\n关系统计:")
            print("-" * 50)
            
            total_rels = 0
            for record in result:
                rel_type = record['type']
                count = record['count']
                total_rels += count
                print(f"  {rel_type:20s} {count:>8,d} 个关系")
            
            print(f"  {'总计':20s} {total_rels:>8,d} 个关系")
            print("=" * 50 + "\n")


if __name__ == "__main__":
    """测试Neo4j管理器"""
    manager = Neo4jManager()
    
    try:
        manager.connect()
        manager.initialize_database()
        manager.get_stats()
    finally:
        manager.close()
