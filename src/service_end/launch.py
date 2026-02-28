from .data import db_init
from .api import create_app, AppDependency
import yaml
import uvicorn


def ensemble_engine_url(user: str, pwd: str, host: str, port: int, db: str):
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"


def main(config_path: str):
    # 加载配置
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # 加载数据库
    I, G, U, D = db_init(
        engine_url=ensemble_engine_url(**config["db_init"]["url"]),
        target_schema=config["db_init"]["target_schema"],
        cache_size=config["db_init"]["cache_size"],
        cache_ttl=config["db_init"]["cache_ttl"],
        clear_exists=config["db_init"]["clear_exists"],
    )

    # 创建 app
    app = create_app(
        dependency=AppDependency(
            insert_operator=I,
            get_operator=G,
            update_operator=U,
            delete_operator=D,
        )
    )
    uvicorn.run(app=app, **config["app"])


if __name__ == "__main__":
    import os
    from pathlib import Path
    config_path = Path(__file__).parent/"config.yaml"
    main(config_path.as_posix())
