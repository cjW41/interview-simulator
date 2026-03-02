from .orm import Base, Base2, Variable
from .operation import insert_operator, get_operator, update_operator, delete_operator
from .utils import VariableInitialDict, insert_execute
from ..exception import ServiceInitException, DatabaseException
from sqlalchemy import inspect, text, insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
import yaml
from pathlib import Path

config_path = Path(__file__).parent.parent/"configs/config.yaml"
with open(config_path, encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

SERVER_DRIVER = "asyncpg"

def ensemble_engine_url(user: str, pwd: str, host: str, port: int, db: str):
    return f"postgresql+{SERVER_DRIVER}://{user}:{pwd}@{host}:{port}/{db}"


engine_url=ensemble_engine_url(**config["url"])
target_schema=config["target_schema"]
clear_exists=config["clear_exists"]


class DataBaseManager:
    """全局数据库访问控制"""

    def __init__(self):
        self.engine: None | AsyncEngine = None
        self.session_maker: None | async_sessionmaker[AsyncSession] = None

    def initiate(self, engine: AsyncEngine):
        self.engine = engine
        self.session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def close(self) -> None:
        assert self.engine
        await self.engine.dispose()

    async def get_session_commit(self):
        """with commit 的 session"""
        # 使用生成器函数，便于 fastapi 依赖注入和管理 session 生命周期
        # 注入 API 后，在 API 内使用 session 无需使用 with 或手动实现生命周期管理
        assert self.session_maker
        async with self.session_maker() as session:
            try:
                yield session       # 开始事务
            except Exception as e:  # 事务执行期间抛出异常
                await session.rollback()
                raise e
            try:
                await session.commit()  # 提交事务
            except Exception as e:      # 事务提交期间抛出异常
                await session.rollback()
                raise DatabaseException(f"error while session commit: {str(e)}")

    async def get_session_wt_commit(self):
        """without commit 的 session"""
        # 使用生成器函数，便于 fastapi 依赖注入和管理 session 生命周期
        # 注入 API 后，在 API 内使用 session 无需使用 with 或手动实现生命周期管理
        assert self.session_maker
        async with self.session_maker() as session:
            yield session  # 开始事务


# 全局唯一实例
db = DataBaseManager()
db.initiate(engine=create_async_engine(url=engine_url))

async def _init_variable_table(session: AsyncSession) -> None:
    """insert data into Variable"""
    data = [
        {"name": k, "value": {"value": v}}
        for k, v in VariableInitialDict.items()
    ]
    dml_stmt = insert(Variable).values(data)
    await insert_execute(
        session=session,
        dml_stmt=dml_stmt,
        table=Variable.__tablename__,
        data=data
    )


async def _execute_clear(session: AsyncSession) -> None:
    """在 clear_exists=True 时，先删表再创建"""
    conn = await session.connection()
    # 普通表
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)
    # Variable
    await conn.run_sync(Base2.metadata.drop_all)
    await conn.run_sync(Base2.metadata.create_all)
    await _init_variable_table(session=session)


async def _execute_not_clear(session: AsyncSession) -> None:
    """在 clear_exists=True 时，只创建不存在的表"""
    conn = await session.connection()
    # 普通表
    await conn.run_sync(Base.metadata.create_all)  # create_all 仅支持同步 Connection
    # Variable
    inspector = await conn.run_sync(inspect)
    if not inspector.has_table(table_name="variable"):
        await conn.run_sync(Base2.metadata.create_all)
        await _init_variable_table(session=session)


async def table_init():
    """检查数据库内表是否存在"""
    engine = db.engine
    assert engine

    async with AsyncSession(engine) as session:
        # 验证数据库是否启动了
        try:
            await session.execute(text("SELECT 'are you ok?'"))
        except SQLAlchemyError as e:
            raise ServiceInitException(
                source_class=e.__class__.__name__,
                message="cannot connect to database"
            ) from e

        # 验证 schema
        try:
            result = await session.execute(text("SELECT current_schema();"))
            current_schemma: str = result.scalar_one()
            if current_schemma != target_schema:
                raise ServiceInitException(
                    source_class=None,
                    message=f"current_schema error: expected '{target_schema}', get '{current_schemma}'"
                )
        except SQLAlchemyError as e:
            raise ServiceInitException(source_class=e.__class__.__name__, message=f"current_schema error: {e}")
    
        # 执行创建
        try:
            if clear_exists:
                await _execute_clear(session=session)
            else:
                await _execute_not_clear(session=session)
        except SQLAlchemyError as e:
            raise ServiceInitException(source_class=e.__class__.__name__, message=str(e)) from e

        # 提交
        try:
            await session.commit()
        except Exception as e:  # 事务提交期间抛出异常
            await session.rollback()
            raise DatabaseException(f"error while session commit: {str(e)}")


__all__ = [
    "table_init", "engine_url", "db",  # 服务端启动
    "insert_operator", "get_operator", "update_operator", "delete_operator",  # APIRouter 调用
]