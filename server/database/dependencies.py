"""
数据库依赖注入
提供FastAPI路由中使用的数据库连接依赖
"""
from typing import Generator
from server.database.sqlite_manager import SQLiteManager
from server.config.settings import settings


def get_db() -> Generator:
    """
    获取数据库连接的依赖注入函数
    
    Yields:
        SQLiteManager: 数据库管理器实例
    """
    db = SQLiteManager(settings.SQLITE_DB_PATH)
    try:
        yield db
    finally:
        db.close()
