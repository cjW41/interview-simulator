# service end launch
from .data import db_init
from .api import create_app, AppDependency
import sys
import asyncio
import yaml
import uvicorn
from pathlib import Path

# 避免 psycopg.InterfaceError: Psycopg cannot use the 'ProactorEventLoop' to run in async mode.
# windows 平台上，asyncio 默认使用 ProactorEventLoop，而 psycopg 需要使用 SelectorEventLoop.
# linux 无需修改
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def ensemble_engine_url(user: str, pwd: str, host: str, port: int, db: str):
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"


if __name__ == "__main__":
    config_path = Path(__file__).parent/"config.yaml"
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # 检查数据库，创建数据库 operator
    C, R, U, D = asyncio.run(
        db_init(
            engine_url=ensemble_engine_url(**config["db_init"]["url"]),
            target_schema=config["db_init"]["target_schema"],
            cache_size=config["db_init"]["cache_size"],
            cache_ttl=config["db_init"]["cache_ttl"],
            clear_exists=config["db_init"]["clear_exists"],
        )
    )

    # 依赖注入，创建 app
    app = create_app(
        dependency=AppDependency(
            insert_operator=C,
            get_operator=R,
            update_operator=U,
            delete_operator=D,
        )
    )

    uvicorn.run(app=app, **config["app"])
