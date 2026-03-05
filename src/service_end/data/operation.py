# data.operation
# 无状态数据库 Operator 类
# 无需进行手动的 session 上下文管理，交给 fastapi
from .cache import with_cache_async, GLOBAL_CACHE, KeyType, KeyFactory
from ..exception import QueryError, TargetedRecordNotFound, UpdateEmpty
from .model import QuestionModel, DomainQuestionBank, JobModel, CVModel, InterviewerModel, LLMCard
from .orm import Variable, Question, Domain, Job, CV, Interviewer, LLM
from .utils import VariableEnum, query_one_record, insert_execute, update_execute, delete_execute, check_empty
from sqlalchemy import exc, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


class InsertOperator:
    """
    将 Pydantic 模型转化成 ORM 对象, insert 到数据库。
    
    APIs
    ```
    [admin] 创建 domain
    domain(model: DomainQuestionBank) -> None

    [admin] 批量插入 Question。domain_name, sub_domain_name 代表 Question 所属领域
    question_batch(domain_name: str, sub_domain_name: str, models: list[QuestionModel]) -> None

    [admin] 创建 job
    job(model: JobModel) -> None

    [admin/user] 批量插入 cv
    cv_batch(models: list[CVModel]) -> None

    [admin] 创建 interviewer
    interviewer(model: InterviewerModel, llm_card: LLMCard) -> None

    [admin] 创建 LLM
    llm(llm_card: LLMCard) -> None
    ```
    """

    async def domain(self, session: AsyncSession, model: DomainQuestionBank):
        """创建不带 Question 的 Domain"""
        # 查询当前已有 domain 数量, 加锁
        dql_stmt = select(Variable).where(Variable.name == VariableEnum.DOMAIN_COUNT.value).with_for_update()
        data = await query_one_record(
            dql_stmt=dql_stmt,
            session=session,
            table=Variable.__tablename__
        )
        domain_count = data.value["value"]  # {"value": number_of_domain}
        if not isinstance(domain_count, int):
            raise TargetedRecordNotFound(
                table=Variable.__tablename__,
                not_found_filter_condition=str(dql_stmt.whereclause)
            )

        # 更新 domain_count
        domain_count += 1
        dml_stmt = update(Variable).where(Variable.name == VariableEnum.DOMAIN_COUNT.value).values(value={"value": domain_count})
        await session.execute(statement=dml_stmt)

        # 插入新 domain 记录
        nrows = len(model.sub_domains)
        data = [
            {
                "domain_id": domain_count,
                "sub_domain_id": idx + 1,
                "domain_name": model.domain,
                "sub_domain_name": model.sub_domains[idx]
            }
            for idx in range(nrows)
        ]
        dml_stmt = insert(Domain).values(data)
        await insert_execute(dml_stmt=dml_stmt, session=session, table=Domain.__tablename__)

        # 更新缓存
        GLOBAL_CACHE.batch_update(    
            {
                KeyFactory.get(
                    KeyType.DOMAIN_SUBDOMAIN,
                    domain_name=domain['domain_name'],
                    sub_domain_name=domain['sub_domain_name']
                ): (domain['domain_id'], domain['sub_domain_id'],)
                for domain in data
            }
        )
        GLOBAL_CACHE.pop(KeyFactory.get(key_type=KeyType.ALL_DOMAIN_NAME))

    @with_cache_async(key_type=KeyType.DOMAIN_SUBDOMAIN)
    async def _get_domain_subdomain_id(
            self,
            session: AsyncSession,
            domain_name: str,
            sub_domain_name: str,
    ) -> tuple[int, int]:
        """获取 `domain_name`,`sub_domain_name` 的 id"""
        dql_stmt = select(Domain).where(
            (Domain.domain_name==domain_name) & (Domain.sub_domain_name==sub_domain_name)
        )
        domain = await query_one_record(
            dql_stmt=dql_stmt,
            session=session,
            table=Domain.__tablename__,
        )
        return (domain.domain_id, domain.sub_domain_id,)

    async def question_batch(
            self,
            session: AsyncSession,
            domain_name: str,
            sub_domain_name: str,
            models: list[QuestionModel]
    ):
        """批量插入 Question。`domain_name`,`sub_domain_name` 代表 Question 所属领域"""
        # 获取 domain/sub_domain 的 id
        domain_id, sub_domain_id = await self._get_domain_subdomain_id(
            session=session,
            domain_name=domain_name,
            sub_domain_name=sub_domain_name
        )
        # 执行插入
        domain_dict = {"domain_id": domain_id, "sub_domain_id": sub_domain_id}
        data = [dict(**domain_dict, **model.model_dump()) for model in models]
        dml_stmt = insert(Question).values(data)
        await insert_execute(session=session, dml_stmt=dml_stmt, table=Question.__tablename__)
    
    async def job(self, session: AsyncSession, model: JobModel):
        """创建 job"""
        data = [model.model_dump()]
        dml_stmt = insert(Job).values(data)
        await insert_execute(session=session, dml_stmt=dml_stmt, table=Job.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_JOB))

    async def cv_batch(self, session: AsyncSession, models: list[CVModel]):
        """批量插入 cv"""
        data = [model.model_dump() for model in models]
        dml_stmt = insert(CV).values(data)
        await insert_execute(session=session, dml_stmt=dml_stmt, table=CV.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_CV_TITLE))
    
    async def interviewer(self, session: AsyncSession, model: InterviewerModel):
        """创建 interviewer"""
        data = [model.model_dump()]
        dml_stmt = insert(Interviewer).values(data)
        await insert_execute(session=session, dml_stmt=dml_stmt, table=Interviewer.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_INTERVIEWER))

    async def llm(self, session: AsyncSession, llm_card: LLMCard):
        """创建 llm"""
        data = [llm_card.model_dump()]
        dml_stmt = insert(LLM).values(data)
        await insert_execute(session=session, dml_stmt=dml_stmt, table=LLM.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_LLM))


class GetOperator:
    """
    通过 ORM 的方式将数据加载为 Model。用于从数据库读取数据。

    APIs:
    ```
    [user] 从数据库按主键 ID 加载一组 QuestionModel
    questions(ids: list[int]) -> list[QuestionModel]

    [admin] 当前数据库内已有领域题库的领域名称
    all_domain_name(self) -> list[str]

    [user] 按照领域名称加载 DomainQuestionBank
    domain_question_bank(domain_name: str) -> DomainQuestionBank

    [admin] 查询当前所有 Job
    all_job() -> list[JobModel]

    [admin/user] 查询一个 cv
    cv(title: str) -> CVModel

    [admin] 查询当前所有 cv 的名称
    all_cv_titles() -> list[str]

    [admin] 查询当前全部 LLM
    all_llm() -> list[LLMCard]

    [admin] 查询当前全部 Interviewer
    all_interviewer() -> list[InterviewerModel]
    ```
    """

    async def questions(self, session: AsyncSession, ids: list[int]) -> list[QuestionModel]:
        """从数据库按主键 ID 加载一组 QuestionModel"""
        dql_stmt = select(Question).where(Question.id_.in_(ids))
        try:
            results = await session.scalars(dql_stmt)
            results = results.all()
            if len(results) < len(ids):
                not_found_ids = set(ids).difference(set(r.id_ for r in results))
                raise TargetedRecordNotFound(
                    table=Question.__tablename__,
                    not_found_filter_condition=f"id={not_found_ids}"
                )
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table=Question.__tablename__,
                filter_condition=f"id={ids}"
            )
        return [QuestionModel.model_validate(q) for q in results]

    @with_cache_async(key_type=KeyType.ALL_DOMAIN_NAME)
    async def all_domain_name(self, session: AsyncSession) -> list[str]:
        """当前数据库内已有领域题库的领域名称"""
        dql_stmt = select(Domain.domain_name).distinct()
        try:
            results = await session.scalars(dql_stmt)
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table=Domain.__tablename__,
                filter_condition=f"none"
            ) from e
        results = results.all()
        return list(results)

    @with_cache_async(key_type=KeyType.QUESTION_BANK)
    async def domain_question_bank(self, session: AsyncSession, domain_name: str) -> DomainQuestionBank:
        """按照领域名称加载 DomainQuestionBank"""
        from collections import defaultdict
        # 查询 (id_, sub_domain_name)
        where_clause = (Domain.domain_name == domain_name)
        dql_stmt = select(Question.id_, Domain.sub_domain_name).join(Domain).where(where_clause)
        try:
            result = await session.execute(dql_stmt)
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table="question.join(domain)",
                filter_condition=str(where_clause)
            ) from e

        # 构建 DomainQuestionBank
        question_ids: dict[str, list[int]] = defaultdict(list)
        for row in result.all():
            question_ids[row.sub_domain_name].append(row.id_)
        return DomainQuestionBank(
            domain=domain_name,
            sub_domains=list(question_ids.keys()),
            question_ids=question_ids
        )

    @with_cache_async(key_type=KeyType.ALL_JOB)
    async def all_job(self, session: AsyncSession) -> list[JobModel]:
        """查询当前所有 Job"""
        dql_stmt = select(Job)
        try:
            results = await session.scalars(dql_stmt)
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table=Job.__tablename__,
                filter_condition=f"none"
            ) from e
        return [JobModel.model_validate(job) for job in results.all()]

    @with_cache_async(key_type=KeyType.CV_TITLE)
    async def cv(self, session: AsyncSession, title: str) -> CVModel:
        """查询一个 cv"""
        dql_stmt = select(CV).where(CV.title == title)
        cv: CV = await query_one_record(
            dql_stmt=dql_stmt,
            session=session,
            table=CV.__tablename__
        )
        return CVModel.model_validate(cv)

    @with_cache_async(key_type=KeyType.ALL_CV_TITLE)
    async def all_cv_titles(self, session: AsyncSession) -> list[str]:
        """查询当前所有 cv 的名称"""
        dql_stmt = select(CV.title)
        try:
            results = await session.scalars(dql_stmt)
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table=CV.__tablename__,
                filter_condition="none"
            ) from e
        return list(results.all())
    
    @with_cache_async(key_type=KeyType.ALL_LLM)
    async def all_llm(self, session: AsyncSession) -> list[LLMCard]:
        """查询当前全部 LLM"""
        dql_stmt = select(LLM)
        try:
            results = await session.scalars(dql_stmt)
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table=LLM.__tablename__,
                filter_condition="none"
            ) from e
        return [LLMCard.model_validate(llm) for llm in results.all()]

    @with_cache_async(key_type=KeyType.ALL_INTERVIEWER)
    async def all_interviewer(self, session: AsyncSession) -> list[InterviewerModel]:
        """查询当前全部 Interviewer"""
        dql_stmt = select(Interviewer)
        try:
            results = await session.scalars(dql_stmt)
        except exc.SQLAlchemyError as e:
            raise QueryError(
                source_class=e.__class__.__name__,
                table=Interviewer.__tablename__,
                filter_condition="none"
            ) from e
        return [InterviewerModel.model_validate(interviewer) for interviewer in results.all()]


class UpdateOperator:
    """
    更新部分表的记录。
    
    APIs
    ```
    [admin] 更新一个 job
    job(model: JobModel) -> None

    [admin] 更新大模型计费
    llm_cost_refresh(model: str, cost_limit: float) -> None

    [admin] 更新 Interviewer 中的模型
    change_interviewer_llm(name: str, new_model_name: str) -> None
    ```
    """

    async def job(self, session: AsyncSession, model: JobModel):
        """更新一个 job"""
        where_clause = (Job.name == model.name)
        await check_empty(session, Job, where_clause)
        
        value = model.model_dump()
        dml_stmt = update(Job).where(where_clause).values(**value)
        await update_execute(
            session=session,
            dml_stmt=dml_stmt,
            table=Job.__tablename__
        )

    async def llm_cost_refresh(self, session: AsyncSession, model: str, cost_limit: float):
        """更新大模型计费"""
        where_clause = (LLM.model == model)
        empty_check_query = select(LLM).where(where_clause)
        results = await session.scalars(empty_check_query)
        if len(results.all()) == 0:
            raise UpdateEmpty(table=Job.__tablename__, filter_condition=str(where_clause))
        
        value = {"cost": 0., "cost_limit": cost_limit}
        dml_stmt = update(LLM).where(where_clause).values(**value)
        await update_execute(
            session=session,
            dml_stmt=dml_stmt,
            table=LLM.__tablename__
        )

    async def change_interviewer_llm(self, session: AsyncSession, name: str, new_model_name: str):
        """更新 Interviewer 中的模型名称"""
        where_clause = (Interviewer.name == name)
        empty_check_query = select(Interviewer).where(where_clause)
        results = await session.scalars(empty_check_query)
        if len(results.all()) == 0:
            raise UpdateEmpty(table=Job.__tablename__, filter_condition=str(where_clause))

        dml_stmt = update(Interviewer).where(where_clause).values(model=new_model_name)
        await update_execute(
            session=session,
            dml_stmt=dml_stmt,
            table=Interviewer.__tablename__,
        )


class DeleteOperator:
    """
    从数据库删除记录。

    APIs
    ```
    [admin] 通过外键级联删除机制删除一个 Domain 对应的领域题库
    domain_question_bank(domain_name: str, sub_domain_name: str | None) -> None

    [admin/user] 删除一个 CV
    cv(title: str) -> None

    [admin] 删除一个 Job
    job(name: str) -> None
    
    [admin] 删除一个 LLM
    llm(model: str) -> None

    [admin] 删除一个 Interviewer
    interviewer(name: str) -> None
    ```
    """

    async def domain_question_bank(
            self,
            session: AsyncSession,
            domain_name: str,
            sub_domain_name: str | None = None
    ):
        """通过外键级联删除机制删除一个 Domain 对应的领域题库"""
        where_clause = (Domain.domain_name == domain_name)
        if sub_domain_name is not None:
            where_clause = where_clause & (Domain.sub_domain_name == sub_domain_name)
        dml_stmt = delete(Domain).where(where_clause)

        await delete_execute(session=session, dml_stmt=dml_stmt, table=Domain.__tablename__)
        GLOBAL_CACHE.pop(
            KeyFactory.get(
                KeyType.DOMAIN_SUBDOMAIN,
                domain_name=domain_name,
                sub_domain_name=sub_domain_name
            )
        )
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_DOMAIN_NAME))
    
    async def cv(self, session: AsyncSession, title: str):
        """删除一个 cv"""
        dml_stmt = delete(CV).where(CV.title == title)
        await delete_execute(session=session, dml_stmt=dml_stmt, table=CV.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.CV_TITLE, title=title))
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_CV_TITLE))

    async def job(self, session: AsyncSession, name: str):
        """删除一个 job"""
        dml_stmt = delete(Job).where(Job.name == name)
        await delete_execute(session=session, dml_stmt=dml_stmt, table=Job.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_JOB))

    async def llm(self, session: AsyncSession, model: str):
        """删除一个 llm"""
        dml_stmt = delete(LLM).where(LLM.model == model)
        await delete_execute(session=session, dml_stmt=dml_stmt, table=LLM.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_LLM))
    
    async def interviewer(self, session: AsyncSession, name: str):
        """删除一个 interviewer"""
        dml_stmt = delete(Interviewer).where(Interviewer.name == name)
        await delete_execute(session=session, dml_stmt=dml_stmt, table=Interviewer.__tablename__)
        GLOBAL_CACHE.pop(KeyFactory.get(KeyType.ALL_INTERVIEWER))


insert_operator = InsertOperator()
get_operator = GetOperator()
update_operator = UpdateOperator()
delete_operator = DeleteOperator()