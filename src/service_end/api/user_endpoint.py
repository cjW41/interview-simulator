# endpoints for user client
from ..data import db
from ..data.operation import insert_operator, get_operator, delete_operator
from ..data.model import CVModel
from ..exception import UploadError
from ..service import parse_cv_workflow
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/user", tags=["User Endpoints"])
SessionDepends_Commit = Depends(db.get_session_commit, use_cache=False)  # with commit
SessionDepends_WT_Commit = Depends(db.get_session_wt_commit, use_cache=False)  # without commit

# data

@router.post("/cv")
async def upload_cv(
    title: str,
    cv_file: UploadFile = File(...),
    session: AsyncSession = SessionDepends_Commit
):
    """上传 CV 并解析"""
    # 上传
    try:
        assert cv_file.filename is not None
        assert cv_file.filename.endswith(".md")
        bytes_content = await cv_file.read()
        content = bytes_content.decode("utf-8")
    except AssertionError as e:
        raise UploadError(message="file name or type incorrect", file_name=str(cv_file.filename)) from e
    except UnicodeDecodeError as e:
        raise UploadError(message="unicode decode error", file_name=str(cv_file.filename)) from e
    
    # 解析
    cv = await parse_cv_workflow(cv_str=content, title=title)
    await insert_operator.cv_batch(session=session, models=[cv])


@router.get("/cv", response_model=CVModel)
async def get_parsed_cv(title: str, session: AsyncSession = SessionDepends_WT_Commit):
    """查询先前上传的 CV"""
    return await get_operator.cv(session=session, title=title)


@router.delete("/cv")
async def delete_cv(title: str, session: AsyncSession = SessionDepends_Commit):
    """删除先前上传的 CV"""
    await delete_operator.cv(session=session, title=title)


# interview





