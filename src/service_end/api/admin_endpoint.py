from ..exception import ServiceEndExceptionBase
from ..data import db
from ..data.operation import insert_operator, get_operator, update_operator, delete_operator
from ..data.model import JobModel, CVModel, LLMCard, InterviewerModel, DomainQuestionBank
from ..service import question_gen_workflow
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/admin", tags=["Admin Endpoints"])
SessionDepends_Commit = Depends(db.get_session_commit, use_cache=False)  # with commit
SessionDepends_WT_Commit = Depends(db.get_session_wt_commit, use_cache=False)  # without commit


# get data

@router.get("/status")
def status(session: AsyncSession = SessionDepends_WT_Commit):
    return {"message": f"interview simulator is alive. dependency '{session.__class__.__name__}' is injected"}


@router.get("/all_domain_name")
async def get_all_domain_name(session: AsyncSession = SessionDepends_WT_Commit) -> list[str]:
    """当前数据库内已有领域题库的领域名称"""
    return await get_operator.all_domain_name(session=session)


@router.get("/all_job", response_model=list[JobModel])
async def get_all_job(session: AsyncSession = SessionDepends_WT_Commit):
    """查询当前所有 Job"""
    return await get_operator.all_job(session=session)


@router.get("/cv", response_model=CVModel)
async def get_cv(title: str, session: AsyncSession = SessionDepends_WT_Commit):
    """查询一个 cv"""
    return await get_operator.cv(session=session, title=title)


@router.get("/all_cv_title")
async def get_all_cv_title(session: AsyncSession = SessionDepends_WT_Commit) -> list[str]:
    """查询当前所有 cv 的名称"""
    return await get_operator.all_cv_titles(session=session)


@router.get("/all_llm", response_model=list[LLMCard])
async def get_all_llm(session: AsyncSession = SessionDepends_WT_Commit):
    """查询当前全部 LLM"""
    return await get_operator.all_llm(session=session)


@router.get("/all_interviewer", response_model=list[InterviewerModel])
async def get_all_interviewer(session: AsyncSession = SessionDepends_WT_Commit):
    """查询当前全部 LLM"""
    return await get_operator.all_interviewer(session=session)


# insert new data

@router.put("/domain")
async def create_domain(
    domain_name: str,
    sub_domain_names: list[str],
    session: AsyncSession = SessionDepends_Commit
) -> None:
    """创建不带 Question 的 Domain"""
    model = DomainQuestionBank(domain=domain_name, sub_domains=sub_domain_names)
    await insert_operator.domain(session=session, model=model)


@router.post("/domain/{domain_name}")
async def create_question_batch(
    domain_name: str,
    sub_domain_names: list[str],
    number: int,
    session: AsyncSession = SessionDepends_Commit
):
    """
    调用 LLM 工作流，批量插入 Question。

    Args:
        domain_name (str): 领域名称
        sub_domain_name (str): 子领域名称
        number (int): 每个“领域-子领域”题目数量
    """
    try:
        for sub_domain_name in sub_domain_names:
            questions = await question_gen_workflow(
                domain_name=domain_name,
                sub_domain_name=sub_domain_name,
                number=number
            )
            await insert_operator.question_batch(
                session=session,
                domain_name=domain_name,
                sub_domain_name=sub_domain_name,
                models=questions,
            )
    except ServiceEndExceptionBase as e:
        await delete_operator.domain_question_bank(session=session, domain_name=domain_name)
        raise e


@router.put("/job/{name}")
async def insert_job(
    name: str,
    job_requirements: list[str],
    job_responsibilities: list[str],
    session: AsyncSession = SessionDepends_Commit
):
    """创建 job"""
    await insert_operator.job(
        session = session,
        model = JobModel(
            name=name,
            job_requirements=job_requirements,
            job_responsibilities=job_responsibilities
        )
    )


@router.put("/cv/{title}")
async def insert_cv_batch(
    cv: list[CVModel],
    session: AsyncSession = SessionDepends_Commit
):
    """批量插入 cv"""
    await insert_operator.cv_batch(session=session, models=cv)


@router.put("/llm/{model}")
async def insert_llm(
    model: str,
    path: str,
    context_window: int,
    key_name: str,
    session: AsyncSession = SessionDepends_Commit
):
    """创建 LLM"""
    await insert_operator.llm(
        session = session,
        llm_card = LLMCard(
            model=model,
            path=path,
            context_window=context_window,
            key_name=key_name,
        )
    )


@router.put("/interview/interviewer/{name}")
async def insert_interviewer(
    name: str,
    llm_name: str,
    system_prompt: str,
    session: AsyncSession = SessionDepends_Commit
):
    """批量插入 CV"""
    await insert_operator.interviewer(
        session = session,
        model = InterviewerModel(
            name=name,
            model=llm_name,
            system_prompt=system_prompt,
        )
    )


# update data

@router.post("/job/{name}")
async def update_job(
    name: str,
    new_job_requirements: list[str],
    new_job_responsibilities: list[str],
    session: AsyncSession = SessionDepends_Commit
):
    """更新一个 job"""
    await update_operator.job(
        session = session,
        model = JobModel(
            name=name,
            job_requirements=new_job_requirements,
            job_responsibilities=new_job_responsibilities
        )
    )


@router.post("/interview/interviewer/{name}")
async def update_interviewer_llm(
    name: str,
    new_model_name: str,
    session: AsyncSession = SessionDepends_Commit
):
    """
    更换 Interviewer 中的模型
    
    Args:
        name (str): 待替换的 interviewer 名称
        new_model_name (str): 被替换的新模型名称
    """
    await update_operator.change_interviewer_llm(
        session=session,
        name=name,
        new_model_name=new_model_name
    )


# delete data

@router.delete("/domain/{domain_name}")
async def delete_question_bank(
    domain_name: str,
    sub_domain_name: str | None = Query(None),
    session: AsyncSession = SessionDepends_Commit
):
    """
    删除一个 Domain 对应的领域题库。
    当不传入 `sub_domain_name`，则删除所有 `domain_name` 下的 `sub_domain_name`
    """
    await delete_operator.domain_question_bank(
        session=session,
        domain_name=domain_name,
        sub_domain_name=sub_domain_name
    )


@router.delete("/cv/{title}")
async def delete_cv(title: str, session: AsyncSession = SessionDepends_Commit):
    """删除一个 CV"""
    await delete_operator.cv(session=session, title=title)


@router.delete("/job/{name}")
async def delete_job(
    name: str,
    session: AsyncSession = SessionDepends_Commit
):
    """删除一个 job"""
    await delete_operator.job(session=session, name=name)


@router.delete("/llm/{model}")
async def delete_llm(
    model: str,
    session: AsyncSession = SessionDepends_Commit
):
    """删除一个 LLM"""
    await delete_operator.llm(session=session, model=model)


@router.delete("/interview/interviewer/{interviewer}")
async def delete_interviewer(
    interviewer: str,
    session: AsyncSession = SessionDepends_Commit
):
    """删除一个 Interviewer"""
    await delete_operator.interviewer(session=session, name=interviewer)

