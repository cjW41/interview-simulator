# data.utils
from ..exception import TragetRecordNotFound, DatabaseException, InsertError, UpdateError
from enum import Enum
from typing import TypeVar
from sqlalchemy import exc, Select, ScalarResult, Insert, Update, Delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class VariableEnum(Enum):
    """常量名称枚举类"""
    DOMAIN_COUNT = "DOMAIN_COUNT"

VariableInitialDict = {"DOMAIN_COUNT": 0} # 常量初始值


async def query_one_record(
        session: AsyncSession,
        dql_stmt: Select[tuple[T]],
        table: str,
        filter_condition: str
    ) -> T:
    """
    查询一条记录并返回。待查询记录满足唯一性约束。

    Args:
        session: 异步 Session 对象
        dql_stmt: Select statement
        table: 表名，用于异常记录
        filter_condition: 查询过滤条件，用于异常记录
    
    Exceptions:
        TragetRecordNotFound: 查询失败, from NoResultFound
        DatabaseException: 其它来自 SQLAlchemy 的异常
    """
    try:
        result = await session.execute(statement=dql_stmt)
        record = result.scalar_one()
    except exc.NoResultFound as e:
        raise TragetRecordNotFound(
            table=table, filter_condition=filter_condition
        ) from e
    except exc.SQLAlchemyError as e:
        raise DatabaseException() from e
    return record


async def session_scalars(session: AsyncSession, dql_stmt: Select[tuple[T]]) -> ScalarResult[T]:
    """使用 `Session.scalars` 方法查询，返回 `ScalarResult`"""
    try:
        return await session.scalars(dql_stmt)
    except exc.SQLAlchemyError as e:
        raise DatabaseException() from e


async def insert_execute(
        session: AsyncSession,
        dml_stmt: Insert,
        data: list[dict],
        table: str
    ) -> None:
    """
    批量插入数据。插入后 commit

    Args:
        session: 异步 Session 对象
        dml_stmt: Insert statement
        data: 插入数据，用于异常记录
        table: 表名，用于异常记录
    
    Exceptions:
        InsertError: 插入期间发生一致性异常、数据异常
        DatabaseException: 其它来自 SQLAlchemy 的异常
    """
    try:
        await session.execute(statement=dml_stmt)
        await session.commit()
    except (exc.IntegrityError, exc.DataError,) as e:
        await session.rollback()
        raise InsertError(source_class=e.__class__.__name__, table=table, data=data)
    except exc.SQLAlchemyError as e:
        await session.rollback()
        raise DatabaseException() from e


async def update_execute(
        session: AsyncSession,
        dml_stmt: Update,
        table: str,
        filter_condition: str,
        value: dict
    ) -> None:
    """
    通过 execute 执行一条 update。更新后 commit
    
    Args:
        session: 异步 Session 对象
        dml_stmt: update statement
        table: 被更新表名称，用于异常记录
        filter_condition: 过滤条件，用于异常记录
        value: 更新的数据对象，用于异常记录
    
    Exceptions:
        InsertError: 更新期间发生一致性异常、数据异常
        DatabaseException: 其它来自 SQLAlchemy 的异常
    """
    try:
        await session.execute(dml_stmt)
        await session.commit()
    except (exc.IntegrityError, exc.DataError,) as e:
        await session.rollback()
        raise UpdateError(
            source_class=e.__class__.__name__,
            table=table,
            filter_condition=filter_condition,
            value=value
        ) from e
    except exc.SQLAlchemyError as e:
        await session.rollback()
        raise DatabaseException() from e


async def delete_execute(session: AsyncSession, dml_stmt: Delete) -> None:
    """删除记录。删除后 commit"""
    try:
        await session.execute(dml_stmt)
        await session.commit()
    except exc.SQLAlchemyError as e:
        await session.rollback()
        raise DatabaseException() from e

