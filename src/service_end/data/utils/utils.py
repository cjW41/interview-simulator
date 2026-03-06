# data.utils
from ...exception.data import (
    QueryError, InsertError, UpdateError, DeleteError,
    IntegrityDataError, UpdateEmpty, TargetedRecordNotFound
)
from .enum_ import SequenceName
from typing import TypeVar
from sqlalchemy import exc, text, Select, Insert, Update, Delete, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def get_next_sequence_val(session: AsyncSession, seq: SequenceName) -> int:
    """获取数据库中一个 Sequence 的下一个值"""
    result: int = await session.scalar(text(f"SELECT nextval('{seq.value}');"))
    return result


async def query_one_record(
        session: AsyncSession,
        dql_stmt: Select[tuple[T]],
        table: str,
) -> T:
    """
    查询一条记录并返回。待查询记录满足唯一性约束。

    Args:
        session: 异步 Session 对象
        dql_stmt: Select statement
        table: 表名，用于异常记录
    """
    try:
        result = await session.execute(statement=dql_stmt)
        record = result.scalar_one()
        return record
    except exc.NoResultFound as e:
        raise TargetedRecordNotFound(
            table=table,
            not_found_filter_condition=str(dql_stmt.whereclause)
        ) from e
    except exc.SQLAlchemyError as e:
        raise QueryError(
            source_class=e.__class__.__name__,
            table=table,
            filter_condition=str(dql_stmt.whereclause)
        ) from e


async def insert_execute(
        session: AsyncSession,
        dml_stmt: Insert,
        table: str
) -> None:
    """
    批量插入数据。插入后 commit

    Args:
        session: 异步 Session 对象
        dml_stmt: Insert statement
        table: 表名，用于异常记录
    
    Exceptions:
        InsertError: 插入期间发生一致性异常、数据异常
        DatabaseException: 其它来自 SQLAlchemy 的异常
    """
    try:
        await session.execute(statement=dml_stmt)
    except (exc.IntegrityError, exc.DataError,) as e:
        raise IntegrityDataError(
            source_class=e.__class__.__name__,
            table=table,
            filter_condition="None",
        ) from e
    except exc.SQLAlchemyError as e:
        raise InsertError(source_class=e.__class__.__name__, table=table) from e


async def check_empty(session, Data, where_clause):
    """在更新前检查 ORM 类 Data 在 where_clause 过滤下是否有查询结果，否则抛出 UpdateEmpty 异常"""
    empty_check_query = select(Data).where(where_clause)
    results = await session.scalars(empty_check_query)
    if len(results.all()) == 0:
        raise UpdateEmpty(table=Data.__tablename__, filter_condition=str(where_clause))


async def update_execute(
        session: AsyncSession,
        dml_stmt: Update,
        table: str,
) -> None:
    """
    通过 execute 执行一条 update。更新后 commit
    
    Args:
        session: 异步 Session 对象
        dml_stmt: Update statement
        table: 被更新表名称，用于异常记录
    
    Exceptions:
        InsertError: 更新期间发生一致性异常、数据异常
        DatabaseException: 其它来自 SQLAlchemy 的异常
    """
    try:
        await session.execute(dml_stmt)
    except (exc.IntegrityError, exc.DataError,) as e:
        raise IntegrityDataError(
            source_class=e.__class__.__name__,
            table=table,
            filter_condition=str(dml_stmt.whereclause),
        ) from e
    except exc.SQLAlchemyError as e:
        raise UpdateError(
            source_class=e.__class__.__name__,
            table=table,
            filter_condition=str(dml_stmt.whereclause),
        ) from e


async def delete_execute(
        session: AsyncSession,
        dml_stmt: Delete,
        table: str,
) -> None:
    """
    删除记录。删除后 commit
    
    Args:
        session: 异步 Session 对象
        dml_stmt: Delete statement
        table: 表名，用于异常记录
    """
    try:
        await session.execute(dml_stmt)
    except exc.IntegrityError as e:
        raise IntegrityDataError(
            source_class=exc.IntegrityError.__name__,
            table=table,
            filter_condition=str(dml_stmt.whereclause),
        ) from e
    except exc.SQLAlchemyError as e:
        raise DeleteError(
            source_class=e.__class__.__name__,
            table=table,
            filter_condition=str(dml_stmt.whereclause),
        ) from e

