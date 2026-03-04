# fastapi 异常处理
#
# - ServiceEndExceptionBase
#     - ServiceInitException  # 无需应用 handle
#     - DBCacheError
#     - UploadError
#     - IntegrityDataError
#     - DatabaseException
#         - IntegrityDataError
#         - QueryError
#         - InsertError
#         - UpdateError
#         - UpdateEmpty
#         - DeleteError
#     - ServiceException

from ..exception import ServiceEndExceptionBase, ServiceException, DatabaseException, DBCacheError, UploadError, UpdateEmpty
from fastapi import status, Request
from fastapi.responses import JSONResponse
import logging


logger = logging.getLogger()


def global_handler(request: Request, e: ServiceEndExceptionBase) -> JSONResponse:
    """服务端异常全局 handler"""
    if isinstance(e, DatabaseException):
        return __handle_DatabaseException(e)
    elif isinstance(e, DBCacheError):
        return __handle_DBCacheError(e)
    elif isinstance(e, ServiceException):
        return __handle_ServiceException(e)
    elif isinstance(e, UploadError):
        return __handle_UploadError(e)
    else:
        logger.fatal(f"Unknown Service-End Exception", exc_info=True)  # 原则上不会直接 raise 异常基类
        return JSONResponse(
            content="Internal Server Error: Unknown",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def __handle_DBCacheError(e: DBCacheError) -> JSONResponse:
    """数据库缓存异常处理"""
    logger.exception(e.message)
    return JSONResponse(
        content="Internal Server Error: DBCache",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def __handle_UploadError(e: UploadError) -> JSONResponse:
    """用户上传异常处理"""
    logger.info("Client File Upload Error")
    return JSONResponse(
        content=f"File Upload Error: {str(e)}",
        status_code=status.HTTP_400_BAD_REQUEST
    )


def __handle_DatabaseException(e: DatabaseException) -> JSONResponse:
    """数据库异常处理"""
    if isinstance(e, UpdateEmpty):
        content=str(e)
        logger.info(content)
        return JSONResponse(
            content=content,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    else:
        logger.exception(f"Database Exception {e.__class__.__name__}: {str(e)}")
        return JSONResponse(
            content="Internal Server Error: Database",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def __handle_ServiceException(e: ServiceException) -> JSONResponse:
    """service 异常处理"""
    ...



