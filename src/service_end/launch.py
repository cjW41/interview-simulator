# # 当使用 psycopg 时
# import sys
# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from .data import db, table_init
from .api import admin_router, user_router
import yaml
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 数据库启动
    await table_init()
    yield
    # 数据库关闭
    await db.close()


def main():
    """服务端启动入口"""
    # 读取启动配置
    config_path = Path(__file__).parent/"configs/config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        app_config = config["app"]
        fastapi_config = config["fastapi"]
    
    # 创建 App
    app = FastAPI(lifespan = lifespan, **fastapi_config)
    app.include_router(admin_router)
    app.include_router(user_router)

    # 启动服务端
    uvicorn.run(app=app, **app_config)
