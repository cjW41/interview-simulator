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
from .orm import Variable, Domain, Question, CV, Job, LLM, Interviewer
from .cache import DBCache  # 数据库缓存
from .utils import VariableInitialDict, insert_execute
from ..exception import ServiceInitException
from sqlalchemy import Engine, create_engine, inspect, text, insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


def db_init(
        engine_url: str,
        cache_size: int,
        cache_ttl: float,
        clear_exists: bool
    ) -> tuple[Engine, InsertOperator, GetOperator, UpdateOperator, DeleteOperator]:
    """
    [服务端启动]
    检查数据库内表是否存在，创建缓存。
    
    Args:
        engine_url (str): 用于 `create_engine`
        cache_size (int): 缓存条数
        cache_ttl (float): 缓存有效时长
        clear_exists (bool):【WARNING】当数据库已经存在是否**删除**后重新创建
    
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
        with Session(bind=engine) as session:
            # 检查创建普通表
            for table in [
                Question,
                Domain,  # parent of Question
                CV,
                Job,
                Interviewer,  # parent of Job
                LLM,  # parent of Interviewer
            ]:
                table_name = table.__tablename__
                if inspector.has_table(table_name=table_name):
                    if clear_exists:
                        session.execute(text(f"TRUNCATE TABLE {table_name}"))
                else:
                    table.__table__.create(engine)  # 无需 checkfirst

            # 单独处理 Variable
            data = [
                {"name": k, "value": {"value": v}}
                for k, v in VariableInitialDict.items()
            ]
            dml_stmt = insert(Variable).values(data)
            if inspector.has_table(table_name=Variable.__tablename__):
                if clear_exists:
                    session.execute(text(f"TRUNCATE TABLE {Variable.__tablename__}"))
                    insert_execute(
                        session=session,
                        dml_stmt=dml_stmt,
                        table=Variable.__tablename__,
                        data=data
                    )
            else:
                Variable.__table__.create(engine)
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
        engine,
        InsertOperator(engine=engine, cache=cache),
        GetOperator(engine=engine, cache=cache),
        UpdateOperator(engine=engine, cache=cache),
        DeleteOperator(engine=engine, cache=cache),
    )


__all__ = [
    "db_init",
    "QuestionModel",
    "DomainQuestionBank",
    "JobModel",
    "WorkExperience",
    "CVBasicInfo",
    "CVModel",
    "LLMCard",
    "InterviewerModel",
]