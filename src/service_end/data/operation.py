# data.operation
import exception as svc_exc
from data.model import QuestionModel, DomainQuestionBank, JobModel, CVModel, InterviewerModel, LLMCard
from data.cache import DBCache
from data.orm import Variable, Question, Domain, Job, CV, Interviewer, LLM
from data.utils import VariableEnum, query_one_record, session_scalars, insert_execute, update_execute, delete_execute
from sqlalchemy import exc, Engine, select, insert, update, delete
from sqlalchemy.orm import Session
from collections import defaultdict


class InsertOperator:
    """
    将 Pydantic 模型转化成 ORM 对象, insert 到数据库。
    
    APIs
    ```
    插入 domain
    domain(model: DomainQuestionBank) -> None

    批量插入 Question。domain_name, sub_domain_name 代表 Question 所属领域
    question_batch(domain_name: str, sub_domain_name: str, models: list[QuestionModel]) -> None

    插入 job
    job(model: JobModel) -> None

    批量插入 cv
    cv_batch(models: list[CVModel]) -> None

    插入 interviewer
    interviewer(model: InterviewerModel, llm_card: LLMCard) -> None

    插入 LLM
    llm(llm_card: LLMCard) -> None
    ```
    """

    def __init__(self, engine: Engine, cache: DBCache):
        self.engine = engine
        self.cache = cache

    def domain(self, model: DomainQuestionBank):
        """插入 domain"""
        with Session(bind=self.engine) as session:
            # 查询当前已有 domain 数量, 加锁
            dql_stmt = select(Variable).where(Variable.name == VariableEnum.DOMAIN_COUNT).with_for_update()
            value = query_one_record(
                dql_stmt=dql_stmt,
                session=session,
                table="variable", filter_condition=f"name={VariableEnum.DOMAIN_COUNT}"
            )
            if isinstance(value, dict):
                domain_count = value["value"]
            else:
                messages = (f"'value' type error: (expected: 'dict', get: '{value.__class__.__name__}')",)
                raise svc_exc.DatabaseException(*messages)
            if not isinstance(domain_count, int):
                messages = (f"'domain_count' type error: (expected: 'int', get: '{domain_count.__class__.__name__}')",)
                raise svc_exc.DatabaseException(*messages)

            # 更新 domain_count
            domain_count += 1
            dml_stmt = (
                update(Variable)
                .where(Variable.name == VariableEnum.DOMAIN_COUNT)
                .values(value={"value": domain_count})
            )
            try:
                session.execute(statement=dml_stmt)
            except exc.SQLAlchemyError as e:
                session.rollback()
                raise svc_exc.DatabaseException() from e

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
            insert_execute(dml_stmt=dml_stmt, session=session, data=data, table="domain")

        # update cache
        self.cache.batch_update(    
            {
                f"{domain['domain_name']}-{domain['sub_domain_name']}":(domain['domain_id'], domain['sub_domain_id'],)
                for domain in data
            }
        )

    def question_batch(self, domain_name: str, sub_domain_name: str, models: list[QuestionModel],):
        """批量插入 Question。`domain_name`,`sub_domain_name` 代表 Question 所属领域"""
        # 获取 domain/sub_domain 的 id
        KEY = f"{domain_name}-{sub_domain_name}"
        cache_data = self.cache.get(KEY)
        if cache_data is not None:
            domain_id, sub_domain_id = cache_data
        else:
            dql_stmt = select(Domain).where(Domain.domain_name==domain_name, Domain.sub_domain_name==sub_domain_name)
            with Session(bind=self.engine) as session:
                domain = query_one_record(
                    dql_stmt=dql_stmt,
                    session=session,
                    table="domain",
                    filter_condition=f"(domain_name={domain_name})&(sub_domain_name={sub_domain_name})"
                )
            domain_id, sub_domain_id = domain.domain_id, domain.sub_domain_id
            self.cache.update(key=KEY, value=(domain_id, sub_domain_id,))
        
        # 执行插入
        domain_dict = {"domain_id": domain_id, "sub_domain_id": sub_domain_id}
        data = [dict(**domain_dict, **model.model_dump()) for model in models]
        dml_stmt = insert(Question).values(data)
        with Session(bind=self.engine) as session:
            insert_execute(dml_stmt=dml_stmt, session=session, data=data, table="question")
    
    def job(self, model: JobModel):
        """插入 job"""
        data = [model.model_dump()]
        dml_stmt = insert(Job).values(data)
        with Session(bind=self.engine) as session:
            insert_execute(dml_stmt=dml_stmt, session=session, data=data, table="job")
        self.cache.pop(key="ALL_JOB")

    def cv_batch(self, models: list[CVModel]):
        """批量插入 cv"""
        data = [model.model_dump() for model in models]
        dml_stmt = insert(CV).values(data)
        with Session(bind=self.engine) as session:
            insert_execute(dml_stmt=dml_stmt, session=session, data=data, table="cv")
        self.cache.pop("ALL_CV_TITLE")
    
    def interviewer(self, model: InterviewerModel, llm_card: LLMCard):
        """插入 interviewer"""
        data = [{"name": model.name, "model": llm_card.model, "system_prompt":model.system_prompt}]
        with Session(bind=self.engine) as session:
            dml_stmt = insert(Interviewer).values(data)
            insert_execute(dml_stmt=dml_stmt, session=session, data=data, table="interviewer")
        self.cache.pop("ALL_INTERVIEWER")

    def llm(self, llm_card: LLMCard):
        """插入 llm"""
        data = [llm_card.model_dump()]
        with Session(bind=self.engine) as session:
            dml_stmt = insert(LLM).values(data)
            insert_execute(dml_stmt=dml_stmt, session=session, data=data, table="llm")
        self.cache.pop("ALL_LLM")


class GetOperator:
    """
    通过 ORM 的方式将数据加载为 Model。用于从数据库读取数据。

    APIs:
    ```
    从数据库按主键 ID 加载一组 QuestionModel
    questions(ids: list[int]) -> list[QuestionModel]

    按照领域名称加载 DomainQuestionBank
    domain_question_bank(domain_name: str) -> DomainQuestionBank

    查询当前所有 Job 的名称/面试官/题库
    all_job() -> list[JobModel]

    查询一个 cv
    cv(title: str) -> CVModel

    查询当前所有 cv 的名称
    all_cv_titles() -> list[str]

    查询当前全部 LLM
    all_llm() -> list[LLMCard]

    查询当前全部 Interviewer
    all_interviewer() -> list[InterviewerModel]
    ```
    """

    def __init__(self, engine: Engine, cache: DBCache):
        self.engine = engine
        self.cache = cache

    def questions(self, ids: list[int]) -> list[QuestionModel]:
        """从数据库按主键 ID 加载一组 QuestionModel"""
        dql_stmt = select(Question).where(Question.id_.in_(ids))
        with Session(bind=self.engine) as session:
            try:
                results = session.scalars(dql_stmt).all()
                if len(results) < len(ids):
                    not_found_ids = set(ids).difference(set(r.id_ for r in results))
                    raise svc_exc.TragetRecordNotFound(table="question", filter_condition=f"id={not_found_ids}")
            except exc.SQLAlchemyError as e:
                raise svc_exc.DatabaseException() from e
        return [QuestionModel.model_validate(q) for q in results]

    def domain_question_bank(self, domain_name: str) -> DomainQuestionBank:
        """按照领域名称加载 DomainQuestionBank"""
        # 查询 (id_, sub_domain_name)
        dql_stmt = select(Question.id_, Domain.sub_domain_name).join(Domain).where(Domain.domain_name == domain_name)
        with Session(bind=self.engine) as session:
            try:
                result = session.execute(dql_stmt)
            except exc.SQLAlchemyError as e:
                raise svc_exc.DatabaseException() from e

        # 构建 DomainQuestionBank
        question_ids: dict[str, list[int]] = defaultdict(list)
        for row in result.all():
            question_ids[row.sub_domain_name].append(row.id_)
        return DomainQuestionBank(
            domain=domain_name,
            sub_domains=list(question_ids.keys()),
            question_ids=question_ids
        )

    def all_job(self) -> list[JobModel]:
        """查询当前所有 Job 的名称/面试官/题库"""
        KEY = "ALL_JOB"
        cache_data = self.cache.get(KEY)
        if cache_data is not None:
            data = cache_data
        else:
            dql_stmt = select(Job)
            with Session(bind=self.engine) as session:
                result = session_scalars(session=session, dql_stmt=dql_stmt)
            data = [JobModel.model_validate(job) for job in result.all()]
            self.cache.update(key=KEY, value=data)
        return data

    def cv(self, title: str) -> CVModel:
        """查询一个 cv"""
        KEY = f"CV-{title}"
        cache_data = self.cache.get(KEY)
        if cache_data is not None:
            data = cache_data
        else:
            dql_stmt = select(CV).where(CV.title == title)
            with Session(bind=self.engine) as session:
                cv: CV = query_one_record(
                    dql_stmt=dql_stmt,
                    session=session,
                    table="cv", filter_condition=f"title={title}"
                )
            data = CVModel.model_validate(cv)
            self.cache.update(key=KEY, value=data)
        return data

    def all_cv_titles(self,) -> list[str]:
        """查询当前所有 cv 的名称"""
        KEY = "ALL_CV_TITLE"
        cache_data = self.cache.get(KEY)
        if cache_data is not None:
            data = cache_data
        else:
            dql_stmt = select(CV.title)
            with Session(bind=self.engine) as session:
                result = session_scalars(session=session, dql_stmt=dql_stmt)
            data = list(result.all())
            self.cache.update(key=KEY, value=data)
        return data
    
    def all_llm(self,) -> list[LLMCard]:
        """查询当前全部 LLM"""
        KEY = "ALL_LLM"
        cache_data = self.cache.get(KEY)
        if cache_data is not None:
            data = cache_data
        else:
            dql_stmt = select(LLM)
            with Session(bind=self.engine) as session:
                result = session_scalars(session=session, dql_stmt=dql_stmt)
            data = [LLMCard.model_validate(llm) for llm in result.all()]
            self.cache.update(key=KEY, value=data)
        return data

    def all_interviewer(self,) -> list[InterviewerModel]:
        """查询当前全部 Interviewer"""
        KEY = "ALL_INTERVIEWER"
        cache_data = self.cache.get(KEY)
        if cache_data is not None:
            data = cache_data
        else:
            dql_stmt = select(Interviewer)
            with Session(bind=self.engine) as session:
                result = session_scalars(session=session, dql_stmt=dql_stmt)
            data = [InterviewerModel.model_validate(interviewer) for interviewer in result]
            self.cache.update(key=KEY, value=data)
        return data


class UpdateOperator:
    """
    更新部分表的记录。
    
    APIs
    ```
    更新一个 job
    job(model: JobModel) -> None

    更新大模型计费
    llm_cost_refresh(model: str, cost_limit: float) -> None

    更新 Interviewer 中的模型名称
    change_interviewer_llm(name: str, new_model_name: str) -> None
    ```
    """

    def __init__(self, engine: Engine, cache: DBCache):
        self.engine = engine
        self.cache = cache

    def job(self, model: JobModel):
        """更新一个 job"""
        value = model.model_dump()
        dml_stmt = update(Job).where(Job.name == model.name).values(**value)
        with Session(bind=self.engine) as session:
            update_execute(
                session=session,
                dml_stmt=dml_stmt,
                table="job", filter_condition=f"name={model.name}", value=value,
            )

    def llm_cost_refresh(self, model: str, cost_limit: float):
        """更新大模型计费"""
        value = {"cost": 0., "cost_limit": cost_limit}
        dml_stmt = update(LLM).where(LLM.model == model).values(**value)
        with Session(bind=self.engine) as session:
            update_execute(
                session=session,
                dml_stmt=dml_stmt,
                table="llm", filter_condition=f"cost=0, cost_limit={cost_limit}", value=value,
            )

    def change_interviewer_llm(self, name: str, new_model_name: str):
        """更新 Interviewer 中的模型名称"""
        dml_stmt = (
            update(Interviewer)
            .where(Interviewer.name == name)
            .values(model=new_model_name)
        )
        with Session(bind=self.engine) as session:
            update_execute(
                session=session,
                dml_stmt=dml_stmt,
                table="interviewer", filter_condition=f"name={name}", value={"model": new_model_name}
            )


class DeleteOperator:
    """
    从数据库删除记录。
    
    APIs
    ```
    通过外键级联删除机制删除一个 Domain 对应的领域题库
    domain_question_bank(domain_name: str, sub_domain_name: str | None) -> None

    删除一个 CV
    cv(title: str) -> None

    删除一个 Job
    job(name: str) -> None
    
    删除一个 LLM
    llm(model: str) -> None

    删除一个 Interviewer
    interviewer(name: str) -> None
    ```
    """

    def __init__(self, engine: Engine, cache: DBCache):
        self.engine = engine
        self.cache = cache

    def domain_question_bank(self, domain_name: str, sub_domain_name: str | None):
        """通过外键级联删除机制删除一个 Domain 对应的领域题库"""
        dml_stmt = (
            delete(Domain)
            .where(Domain.domain_name == domain_name, Domain.sub_domain_name == sub_domain_name)
        )
        with Session(bind=self.engine) as session:
            delete_execute(session=session, dml_stmt=dml_stmt)
        self.cache.pop(key=f"{domain_name}-{sub_domain_name}")
    
    def cv(self, title: str):
        """删除一个 cv"""
        dml_stmt = delete(CV).where(CV.title == title)
        with Session(bind=self.engine) as session:
            delete_execute(session=session, dml_stmt=dml_stmt)
        self.cache.pop(key=f"CV-{title}")
        self.cache.pop(key="ALL_CV_TITLE")

    def job(self, name: str):
        """删除一个 job"""
        dml_stmt = delete(Job).where(Job.name == name)
        with Session(bind=self.engine) as session:
            delete_execute(session=session, dml_stmt=dml_stmt)
        self.cache.pop(key="ALL_JOB")

    def llm(self, model: str):
        """删除一个 llm"""
        dml_stmt = delete(LLM).where(LLM.model == model)
        with Session(bind=self.engine) as session:
            delete_execute(session=session, dml_stmt=dml_stmt)
        self.cache.pop(key="ALL_LLM")
    
    def interviewer(self, name: str):
        """删除一个 interviewer"""
        dml_stmt = delete(Interviewer).where(Interviewer.name == name)
        with Session(bind=self.engine) as session:
            delete_execute(session=session, dml_stmt=dml_stmt)
        self.cache.pop(key="ALL_INTERVIEWER")


