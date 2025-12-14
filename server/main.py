"""
FastAPI主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api import dynasties, emperors, events, persons, timeline, search, statistics, relations
from server.config.settings import settings

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(dynasties.router, prefix="/api/v1/dynasties", tags=["朝代"])
app.include_router(emperors.router, prefix="/api/v1/emperors", tags=["皇帝"])
app.include_router(events.router, prefix="/api/v1/events", tags=["事件"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["人物"])
app.include_router(timeline.router, prefix="/api/v1/timeline", tags=["时间轴"])
app.include_router(search.router, prefix="/api/v1/search", tags=["搜索"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["统计"])
app.include_router(relations.router, prefix="/api/v1/relations", tags=["关系图谱"])


@app.get("/", tags=["根路径"])
async def root():
    """根路径，返回API信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
