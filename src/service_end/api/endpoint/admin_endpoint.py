from ...exception import ServiceException
from ...data import InsertOperator, GetOperator, UpdateOperator, DeleteOperator
from ...data.model import JobModel, CVModel, LLMCard, InterviewerModel, DomainQuestionBank, QuestionModel, InterviewArrangement
from ...api.dependency import DependsFn
from ...service import question_gen_workflow
from fastapi import APIRouter, Query

router = APIRouter(prefix="/admin", tags=["Admin Endpoints"])


# get data

@router.get("/status")
def status(dependency: GetOperator = DependsFn.GetOperator):
    return {"message": f"interview simulator is alive. dependency '{dependency.__class__.__name__}' is injected"}


@router.get("/all_domain_name")
async def get_all_domain_name(get_operator: GetOperator = DependsFn.GetOperator) -> list[str]:
    """当前数据库内已有领域题库的领域名称"""
    return await get_operator.all_domain_name()


@router.get("/all_job", response_model=list[JobModel])
async def get_all_job(get_operator: GetOperator = DependsFn.GetOperator):
    """查询当前所有 Job"""
    return await get_operator.all_job()


@router.get("/cv", response_model=CVModel)
async def get_cv(title: str, get_operator: GetOperator = DependsFn.GetOperator):
    """查询一个 cv"""
    return await get_operator.cv(title=title)


@router.get("/all_cv_title")
async def get_all_cv_title(get_operator: GetOperator = DependsFn.GetOperator) -> list[str]:
    """查询当前所有 cv 的名称"""
    return await get_operator.all_cv_titles()


@router.get("/all_llm", response_model=list[LLMCard])
async def get_all_llm(get_operator: GetOperator = DependsFn.GetOperator):
    """查询当前全部 LLM"""
    return await get_operator.all_llm()


@router.get("/all_interviewer", response_model=list[InterviewerModel])
async def get_all_interviewer(get_operator: GetOperator = DependsFn.GetOperator):
    """查询当前全部 LLM"""
    return await get_operator.all_interviewer()


# insert new data

@router.put("/domain")
async def create_domain(
    domain_name: str,
    sub_domain_names: list[str],
    insert_operator: InsertOperator = DependsFn.InsertOperator
) -> None:
    """创建不带 Question 的 Domain"""
    model = DomainQuestionBank(domain=domain_name, sub_domains=sub_domain_names)
    await insert_operator.domain(model=model)


@router.post("/domain/{domain_name}")
async def create_question_batch(
    domain_name: str,
    sub_domain_names: list[str],
    number: int,
    insert_operator: InsertOperator = DependsFn.InsertOperator,
    delete_operator: DeleteOperator = DependsFn.DeleteOperator,
):
    """
    调用 LLM 工作流，批量插入 Question。
    `domain_name`,`sub_domain_name` 代表 Question 所属领域
    """
    try:
        for sub_domain_name in sub_domain_names:
            questions = await question_gen_workflow(
                domain_name=domain_name,
                sub_domain_name=sub_domain_name,
                number=number
            )
            await insert_operator.question_batch(
                domain_name=domain_name,
                sub_domain_name=sub_domain_name,
                models=questions,
            )
    except ServiceException as e:
        await delete_operator.domain_question_bank(domain_name=domain_name)
        raise e


@router.put("/job/{name}")
async def insert_job(
    name: str,
    job_requirements: list[str],
    job_responsibilities: list[str],
    insert_operator: InsertOperator = DependsFn.InsertOperator
):
    """创建 job"""
    await insert_operator.job(
        JobModel(
            name=name,
            job_requirements=job_requirements,
            job_responsibilities=job_responsibilities
        )
    )


@router.put("/cv/{title}")
async def insert_cv_batch(
    cv: list[CVModel],
    insert_operator: InsertOperator = DependsFn.InsertOperator
):
    """批量插入 cv"""
    await insert_operator.cv_batch(models=cv)


@router.put("/llm/{model}")
async def insert_llm(
    model: str,
    is_local: bool,
    path: str,
    cost: float = Query(default=0.),
    cost_limit: float = Query(default=1E8),
    insert_operator: InsertOperator = DependsFn.InsertOperator
):
    """创建 LLM"""
    await insert_operator.llm(
        LLMCard(
            model=model,
            is_local=is_local,
            path=path,
            cost=cost,
            cost_limit=cost_limit
        )
    )


@router.put("/interview/interviewer/{name}")
async def insert_interviewer(
    name: str,
    llm_name: str,
    system_prompt: str,
    insert_operator: InsertOperator = DependsFn.InsertOperator
):
    """批量插入 CV"""
    await insert_operator.interviewer(
        InterviewerModel(
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
    update_operator: UpdateOperator = DependsFn.UpdateOperator
):
    """更新一个 job"""
    await update_operator.job(
        JobModel(
            name=name,
            job_requirements=new_job_requirements,
            job_responsibilities=new_job_responsibilities
        )
    )


@router.post("/llm/{model}")
async def update_llm_cost_limit(
    model: str,
    new_cost_limit: float,
    update_operator: UpdateOperator = DependsFn.UpdateOperator
):
    """重置一个 LLM 的 cost"""
    await update_operator.llm_cost_refresh(model=model, cost_limit=new_cost_limit)


@router.post("/interview/interviewer/{name}")
async def update_interviewer_llm(
    name: str,
    new_model_name: str,
    update_operator: UpdateOperator = DependsFn.UpdateOperator
):
    """更换 Interviewer 中的模型"""
    await update_operator.change_interviewer_llm(name=name, new_model_name=new_model_name)


# delete data

@router.delete("/domain/{domain_name}")
async def delete_question_bank(
    domain_name: str,
    sub_domain_name: str | None = Query(None),
    delete_operator: DeleteOperator = DependsFn.DeleteOperator
):
    """
    删除一个 Domain 对应的领域题库。
    当不传入 `sub_domain_name`，则删除所有 `domain_name` 下的 `sub_domain_name`
    """
    await delete_operator.domain_question_bank(
        domain_name=domain_name,
        sub_domain_name=sub_domain_name
    )


@router.delete("/cv/{title}")
async def delete_cv(title: str, delete_operator: DeleteOperator = DependsFn.DeleteOperator):
    """删除一个 CV"""
    await delete_operator.cv(title=title)


@router.delete("/job/{name}")
async def delete_job(
    name: str,
    delete_operator: DeleteOperator = DependsFn.DeleteOperator
):
    """删除一个 job"""
    await delete_operator.job(name=name)


@router.delete("/llm/{model}")
async def delete_llm(
    model: str,
    delete_operator: DeleteOperator = DependsFn.DeleteOperator
):
    """删除一个 LLM"""
    await delete_operator.llm(model=model)


@router.delete("/interview/interviewer/{interviewer}")
async def delete_interviewer(
    interviewer: str,
    delete_operator: DeleteOperator = DependsFn.DeleteOperator
):
    """删除一个 Interviewer"""
    await delete_operator.interviewer(name=interviewer)

