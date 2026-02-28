from ...exception import ServiceException
from ...data import InsertOperator, GetOperator, UpdateOperator, DeleteOperator
from ...api.dependency import DependsFn
from fastapi import APIRouter


router = APIRouter(prefix="/admin", tags=["Admin Endpoints"])

@router.get("/status")
def status(dependency: GetOperator = DependsFn.GetOperator):
    return {"message": f"interview simulator is alive. dependency '{dependency.__class__.__name__}' is injected"}


# @router.get("/questions")
# def get_questions(ids: list[int]):
    

