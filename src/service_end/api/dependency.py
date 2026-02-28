import exception as svc_exc
from data import GetOperator, InsertOperator, UpdateOperator, DeleteOperator
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel


# 通过属性注入依赖的 App 类
class DependencyModel(BaseModel):
    get_operator: GetOperator
    insert_operator: InsertOperator
    update_operator: UpdateOperator
    delete_operator: DeleteOperator


class FastAPIwithDI(FastAPI):
    
    def inject_my_dependency(self, dependency: DependencyModel):
        """将 DependencyModel 对象作为属性 dependency 添加到 app 上"""
        if hasattr(self, "dependency"):
            message = "Dependency Injection Error. Attribute 'dependency' already exists."
            raise svc_exc.ServiceInitException(source_class=None, message=message)
        self.__setattr__("dependency", dependency)


# 函数注入 APIRouter 依赖的 Get/Insert/Update/DeleteOperator
def examin_request(rq: Request) -> DependencyModel:
    """从 Request 验证并提取 DependencyModel"""
    if not isinstance(rq.app, FastAPIwithDI):
        raise svc_exc.ServiceEndException()
    if not hasattr(rq.app, "dependency"):
        raise svc_exc.ServiceEndException()
    dependency = getattr(rq.app, "dependency")
    if not isinstance(dependency, DependencyModel):
        raise svc_exc.ServiceEndException()
    return dependency


def _getInsertOperator(rq: Request) -> InsertOperator:
    dependency = examin_request(rq=rq)
    return dependency.insert_operator


def _getGetOperator(rq: Request) -> GetOperator:
    dependency = examin_request(rq=rq)
    return dependency.get_operator


def _getUpdateOperator(rq: Request) -> UpdateOperator:
    dependency = examin_request(rq=rq)
    return dependency.update_operator


def _getDeleteOperator(rq: Request) -> DeleteOperator:
    dependency = examin_request(rq=rq)
    return dependency.delete_operator


class DependsFn:
    """封装 FastAPI 所有 Depends"""
    InsertOperator = Depends(_getInsertOperator, use_cache=False)
    GetOperator = Depends(_getGetOperator, use_cache=False)
    UpdateOperator = Depends(_getUpdateOperator, use_cache=False)
    DeleteOperator = Depends(_getDeleteOperator, use_cache=False)

