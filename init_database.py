#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于初始化SQLite和Neo4j数据库
"""
import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from server.database.sqlite_manager import SQLiteManager
from crawler.pipelines.neo4j_pipeline import Neo4jManager


def init_sqlite():
    """初始化SQLite数据库"""
    print("=" * 60)
    print("开始初始化SQLite数据库...")
    print("=" * 60)
    
    # 创建数据库目录
    db_path = project_root / 'server' / 'database' / 'historygogo.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取初始化脚本
    init_script_path = project_root / 'server' / 'database' / 'init_sqlite.sql'
    
    if not init_script_path.exists():
        print(f"❌ 错误：初始化脚本不存在：{init_script_path}")
        return False
    
    try:
        # 使用SQLiteManager初始化
        manager = SQLiteManager(str(db_path))
        manager.initialize_database()
        
        print("✓ SQLite数据库初始化成功")
        print(f"  数据库路径：{db_path}")
        
        # 显示表列表
        tables = manager.get_all_tables()
        print(f"  已创建表：{', '.join([t for t in tables if not t.startswith('sqlite_')])}")
        
        # 显示统计信息
        stats = {
            'dynasties': manager.count_records('dynasties'),
            'emperors': manager.count_records('emperors'),
            'events': manager.count_records('events'),
            'persons': manager.count_records('persons')
        }
        print(f"  数据统计：{stats}")
        
        manager.close()
        return True
        
    except Exception as e:
        print(f"❌ SQLite初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def init_neo4j():
    """初始化Neo4j数据库"""
    print("\n" + "=" * 60)
    print("开始初始化Neo4j数据库...")
    print("=" * 60)
    
    try:
        # 从配置文件读取Neo4j连接信息
        from crawler.config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
        
        # 创建Neo4j管理器
        manager = Neo4jManager(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # 读取初始化脚本
        init_script_path = project_root / 'server' / 'database' / 'init_neo4j.cypher'
        
        if not init_script_path.exists():
            print(f"❌ 错误：初始化脚本不存在：{init_script_path}")
            manager.close()
            return False
        
        # 执行初始化
        manager.initialize_database(str(init_script_path))
        
        print("✓ Neo4j数据库初始化成功")
        print(f"  连接URI：{NEO4J_URI}")
        
        # 显示统计信息
        stats = manager.get_statistics()
        print(f"  数据统计：{stats}")
        
        manager.close()
        return True
        
    except ImportError:
        print("⚠ 警告：无法导入Neo4j配置，跳过Neo4j初始化")
        print("  请确保已安装neo4j驱动：pip install neo4j")
        return False
    except Exception as e:
        print(f"❌ Neo4j初始化失败：{e}")
        print("  请确保Neo4j服务已启动，并检查连接配置")
        import traceback
        traceback.print_exc()
        return False


def check_neo4j_connection():
    """检查Neo4j连接"""
    try:
        from crawler.config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception as e:
        return False


def main():
    """主函数"""
    print("\n" + "🚀 HistoryGogo 数据库初始化工具".center(60, "="))
    print()
    
    success = True
    
    # 初始化SQLite
    if not init_sqlite():
        success = False
    
    # 检查Neo4j连接
    if check_neo4j_connection():
        if not init_neo4j():
            success = False
    else:
        print("\n" + "=" * 60)
        print("⚠ 跳过Neo4j初始化")
        print("=" * 60)
        print("  Neo4j服务未运行或连接配置有误")
        print("  如需使用Neo4j，请：")
        print("  1. 安装Neo4j Desktop或Neo4j服务器")
        print("  2. 启动Neo4j服务")
        print("  3. 在crawler/config/settings.py中配置连接信息")
        print("  4. 重新运行此脚本")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 数据库初始化完成！")
    else:
        print("⚠ 数据库初始化部分失败，请查看上述错误信息")
    print("=" * 60)
    print()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
