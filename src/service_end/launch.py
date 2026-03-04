# # 当使用 psycopg 时
# import sys
# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
from .configs import APP_KWARGS, FASTAPI_KWARGS
from .log import shutdown_log, setup_log
setup_log()

from .data import db, table_init
from .api import admin_router, user_router, global_handler
from .exception import ServiceEndExceptionBase
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware

api_logger = logging.getLogger("api")

# 创建 App
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 数据库启动
    await table_init()
    yield
    # 数据库关闭
    await db.close()
    shutdown_log()

app = FastAPI(lifespan = lifespan, **FASTAPI_KWARGS)

@app.exception_handler(ServiceEndExceptionBase)
async def handler(request: Request, e: ServiceEndExceptionBase) -> JSONResponse:
    return global_handler(request=request, e=e)


# 添加中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    api_logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.*.*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加路由
app.include_router(admin_router)
app.include_router(user_router)


# 声明入口
def main():
    """服务端启动入口"""
    try:
        uvicorn.run(app="src.service_end.launch:app", **APP_KWARGS)
    finally:
        shutdown_log()  # 确保日志队列被关闭
