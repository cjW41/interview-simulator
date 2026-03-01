# endpoints for user client
from ...api.dependency import DependsFn
from ...data import InsertOperator, GetOperator, DeleteOperator
from ...data.model import CVModel
from ...exception import UploadError
from ...service import parse_cv_workflow
from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/user", tags=["User Endpoints"])


# data

@router.post("/cv")
async def upload_cv(
    title: str,
    cv_file: UploadFile = File(...),
    insert_operator: InsertOperator = DependsFn.InsertOperator
):
    """上传 CV 并解析"""
    # 上传
    try:
        assert cv_file.filename is not None
        assert cv_file.filename.endswith(".md")
        bytes_content = await cv_file.read()
        content = bytes_content.decode("utf-8")
    except AssertionError as e:
        raise UploadError() from e
    except UnicodeDecodeError as e:
        raise UploadError() from e
    
    # 解析
    cv = await parse_cv_workflow(cv_str=content, title=title)
    await insert_operator.cv_batch(models=[cv])


@router.get("/cv", response_model=CVModel)
async def get_parsed_cv(title: str, get_operator: GetOperator = DependsFn.GetOperator):
    """查询先前上传的 CV"""
    return await get_operator.cv(title=title)


@router.delete("/cv")
async def delete_cv(title: str, delete_operator: DeleteOperator = DependsFn.DeleteOperator):
    """删除先前上传的 CV"""
    await delete_operator.cv(title=title)


# interview





