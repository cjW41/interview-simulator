from .base import ServiceEndExceptionBase, ServiceException


class LLMResponseError(ServiceException):
    """大模型响应存在异常"""
    pass


class ContextWindowError(ServiceException):
    """ContextWindow 抛出的异常"""
    pass
