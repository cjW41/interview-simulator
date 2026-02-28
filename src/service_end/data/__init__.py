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
from .orm import Base, Base2, Variable, Domain, Question, CV, Job, LLM, Interviewer
from .cache import DBCache  # 数据库缓存
from .utils import VariableInitialDict, insert_execute
from ..exception import ServiceInitException
from sqlalchemy import Engine, create_engine, inspect, text, insert, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


def db_init(
        engine_url: str,
        cache_size: int,
        cache_ttl: float,
        clear_exists: bool
    ) -> tuple[InsertOperator, GetOperator, UpdateOperator, DeleteOperator]:
    """
    [服务端启动]
    检查数据库内表是否存在，创建缓存。
    
    Args:
        engine_url (str): 用于 `create_engine`
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
    engine = create_engine(engine_url)
    inspector = inspect(engine)
    cache = DBCache(size=cache_size, ttl=cache_ttl)

    try:
        # 普通表
        if clear_exists:
            Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # 单独处理 Variable
        if clear_exists or not inspector.has_table(table_name=Variable.__tablename__):  # 是否进行创建
            Base2.metadata.create_all(bind=engine)
            with Session(bind=engine) as session:
                data = [
                    {"name": k, "value": {"value": v}}
                    for k, v
                    in VariableInitialDict.items()
                ]
                dml_stmt = insert(Variable).values(data)
                insert_execute(
                    session=session,
                    dml_stmt=dml_stmt,
                    table=Variable.__tablename__,
                    data=data
                )
    except SQLAlchemyError as e:
        raise ServiceInitException(
            source_class=e.__class__.__name__,
            message=str(e)
        ) from e

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