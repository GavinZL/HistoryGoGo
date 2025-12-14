"""
SQLite数据库管理器
提供数据库连接和初始化功能
"""

import sqlite3
from pathlib import Path
from typing import Optional
import os


class SQLiteManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为 crawler/data/historygogo.db
        """
        if db_path is None:
            # 默认数据库路径
            base_dir = Path(__file__).parent.parent.parent
            db_path = base_dir / 'crawler' / 'data' / 'historygogo.db'
        
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        
        # 确保数据库目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """建立数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            # 设置row_factory以返回字典
            self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self):
        """初始化数据库（创建表结构）"""
        sql_file = Path(__file__).parent / 'init_sqlite.sql'
        
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL初始化文件不存在: {sql_file}")
        
        # 读取SQL脚本
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本
        conn = self.connect()
        try:
            conn.executescript(sql_script)
            conn.commit()
            print(f"✅ 数据库初始化成功: {self.db_path}")
        except Exception as e:
            conn.rollback()
            print(f"❌ 数据库初始化失败: {str(e)}")
            raise
    
    def execute(self, sql: str, params: tuple = None):
        """执行SQL语句"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return cursor
        except Exception as e:
            conn.rollback()
            raise e
    
    def execute_many(self, sql: str, params_list: list):
        """批量执行SQL语句"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
    
    def fetch_one(self, sql: str, params: tuple = None):
        """查询单条记录"""
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchone()
    
    def fetch_all(self, sql: str, params: tuple = None):
        """查询多条记录"""
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    def get_table_info(self, table_name: str):
        """获取表结构信息"""
        sql = f"PRAGMA table_info({table_name})"
        return self.fetch_all(sql)
    
    def get_all_tables(self):
        """获取所有表名"""
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        rows = self.fetch_all(sql)
        return [row[0] for row in rows]
    
    def count_records(self, table_name: str):
        """统计表中的记录数"""
        sql = f"SELECT COUNT(*) FROM {table_name}"
        result = self.fetch_one(sql)
        return result[0] if result else 0
    
    def vacuum(self):
        """优化数据库（回收空间）"""
        conn = self.connect()
        conn.execute("VACUUM")
        print("✅ 数据库优化完成")


def init_database(db_path: str = None):
    """
    初始化数据库的便捷函数
    
    Args:
        db_path: 数据库文件路径
    """
    manager = SQLiteManager(db_path)
    manager.initialize_database()
    manager.close()


def get_database_stats(db_path: str = None):
    """
    获取数据库统计信息
    
    Args:
        db_path: 数据库文件路径
    """
    manager = SQLiteManager(db_path)
    
    print("\n" + "=" * 50)
    print("数据库统计信息")
    print("=" * 50)
    print(f"数据库路径: {manager.db_path}")
    
    if not manager.db_path.exists():
        print("❌ 数据库文件不存在")
        return
    
    file_size = manager.db_path.stat().st_size / 1024  # KB
    print(f"文件大小: {file_size:.2f} KB")
    
    print("\n表统计:")
    print("-" * 50)
    
    tables = manager.get_all_tables()
    total_records = 0
    
    for table in tables:
        if not table.startswith('sqlite_'):
            count = manager.count_records(table)
            total_records += count
            print(f"  {table:30s} {count:>8,d} 条记录")
    
    print("-" * 50)
    print(f"  {'总计':30s} {total_records:>8,d} 条记录")
    print("=" * 50 + "\n")
    
    manager.close()


if __name__ == "__main__":
    """测试数据库管理器"""
    import sys
    
    # 初始化数据库
    print("初始化数据库...")
    init_database()
    
    # 显示统计信息
    get_database_stats()
