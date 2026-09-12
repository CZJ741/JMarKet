from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api.endpoints import router as api_router

# 自动建表（轻量化 SQLite 方案）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="黄师互助平台后端 API，服务黄冈师范学院校园 C2C 自助发布与互助接单"
)

# 允许跨域（方便本地联调）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "disclaimer": settings.DISCLAIMER,
        "docs_url": "/docs"
    }
