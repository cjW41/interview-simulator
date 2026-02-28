from .model import (       # Pydantic Models:
    QuestionModel,       # 领域面试问题
    DomainQuestionBank,  # 领域题库
    JobModel,            # 岗位
    WorkExperience,      # 工作经历, CVBasicInfo 一部分
    CVBasicInfo,         # 简历基本数据, CVModel 一部分
    CVModel,             # 简历
    LLMCard,             # 大模型
    InterviewerModel     # AI 面试官
)
from .operation import InsertOperator, GetOperator, UpdateOperator, DeleteOperator  # 数据库 CRUD API
from .orm import Base, Base2, Variable
from .cache import DBCache  # 数据库缓存
from .utils import VariableInitialDict, insert_execute
from ..exception import ServiceInitException
from sqlalchemy import Engine, create_engine, inspect, text, insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.exc import SQLAlchemyError


async def _init_variable_table(engine: AsyncEngine) -> None:
    """insert data into Variable"""
    data = [
        {"name": k, "value": {"value": v}}
        for k, v in VariableInitialDict.items()
    ]
    async with AsyncSession(bind=engine) as session:
        dml_stmt = insert(Variable).values(data)
        await insert_execute(
            session=session,
            dml_stmt=dml_stmt,
            table=Variable.__tablename__,
            data=data
        )


async def _execute_clear(engine: AsyncEngine, sync_engine: Engine) -> None:
    """在 clear_exists=True 时，先删表再创建"""
    # 普通表
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    # Variable
    Base2.metadata.drop_all(bind=sync_engine)
    Base2.metadata.create_all(bind=sync_engine)
    await _init_variable_table(engine=engine)


async def _execute_not_clear(engine: AsyncEngine, sync_engine: Engine) -> None:
    """在 clear_exists=True 时，只创建不存在的表"""
    # 普通表
    Base.metadata.create_all(bind=sync_engine)
    # Variable
    inspector = inspect(sync_engine)
    if not inspector.has_table(table_name="variable"):
        Base2.metadata.create_all(bind=sync_engine)
        await _init_variable_table(engine=engine)


async def db_init(
        engine_url: str,
        target_schema: str,
        cache_size: int,
        cache_ttl: float,
        clear_exists: bool,
    ) -> tuple[InsertOperator, GetOperator, UpdateOperator, DeleteOperator]:
    """
    [服务端启动]
    检查数据库内表是否存在，创建缓存。
    
    Args:
        engine_url (str): 用于 `create_engine`
        target_schema (str): 数据库表所在 schema。若与 current_schema 不匹配，则终止服务端启动。
        cache_size (int): 缓存条数
        cache_ttl (float): 缓存有效时长
        clear_exists (bool):【WARNING】是否**删除**当前已经存在的表后重新创建
    
    Return:
        Engine: 数据库引擎
        InsertOperator: 数据库插入 API
        GetOperator: 数据库查询 API
        UpdateOperator: 数据库更新 API
        DeleteOperator: 数据库删除 API
    """
    sync_engine = create_engine(engine_url)
    engine = create_async_engine(engine_url)
    
    # 验证 schema
    with sync_engine.connect() as conn:
        try:
            current_schemma: str = conn.execute(text("SELECT current_schema();")).scalar_one()
        except SQLAlchemyError as e:
            raise ServiceInitException(source_class=e.__class__.__name__, message=f"current_schema error: {e}")
    if current_schemma != target_schema:
        raise ServiceInitException(source_class=None, message=f"current_schema error: expected '{target_schema}', get '{current_schemma}'")
    
    # 执行创建
    try:
        if clear_exists:
            await _execute_clear(engine=engine, sync_engine=sync_engine)
        else:
            await _execute_not_clear(engine=engine, sync_engine=sync_engine)
    except SQLAlchemyError as e:
        raise ServiceInitException(source_class=e.__class__.__name__, message=str(e)) from e

    # 返回封装了引擎和缓存的 operator
    cache = DBCache(size=cache_size, ttl=cache_ttl)
    
    return (
        InsertOperator(engine=engine, cache=cache),
        GetOperator(engine=engine, cache=cache),
        UpdateOperator(engine=engine, cache=cache),
        DeleteOperator(engine=engine, cache=cache),
    )


__all__ = [
    "db_init",
    # model
    "QuestionModel", "DomainQuestionBank", "JobModel", "WorkExperience", "CVBasicInfo", "CVModel", "LLMCard", "InterviewerModel",
    # operation
    "InsertOperator", "GetOperator", "UpdateOperator", "DeleteOperator"
]