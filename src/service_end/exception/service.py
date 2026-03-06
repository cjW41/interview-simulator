from .base import ServiceEndExceptionBase, ServiceException


class LLMEmptyResponse(ServiceException):
    """大模型响应为空"""
    pass

