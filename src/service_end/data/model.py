# data.model
from pydantic import BaseModel, Field, ConfigDict


class ORMBaseModel(BaseModel):
    # 让 model_validate 支持 ORM -> Pydantic
    model_config = ConfigDict(from_attributes=True)


# 领域题库
class QuestionModel(ORMBaseModel):
    question: str
    answer: str          # 参考回答
    criterion_low: str   # 评价标准：坏回答
    criterion_mid: str   # 评价标准：一般回答
    criterion_high: str  # 评价标准：好回答


class DomainQuestionBank(BaseModel):
    """
    领域题库

    - 将新领域插入数据库时，需使用这个对象调用数据插入 API。此时，只需设置好 domain, sub_domains 字段，无需提供 question_ids。
    - 从数据库查询已创建好的领域题库时，会将数据库内 domain-sub_domains 对应的所有 question 的主键查询出来，
      存放到 question_ids 内。
    """
    domain: str = Field(max_length=20)             # 领域
    sub_domains: list[str] = Field(max_length=20)  # 子领域
    question_ids: dict[str, list[int]] | None = Field(default=None)  # key: sub_domain, val: question_indices_list


# 岗位
class JobModel(ORMBaseModel):
    name: str = Field(max_length=20)                      # 名称
    job_requirements: list[str]      # 岗位要求
    job_responsibilities: list[str]  # 岗位职责
    question_banks: list[dict[str, str]]  # {'domain': domain_name, 'sub_domain': sub_domain_name}
    interviewer_name: str            # 面试官名称


# 简历
class WorkExperience(BaseModel):
    """一个岗位的工作经历"""
    job: str
    year: float
    duty: str  # 工作经历描述


class CVBasicInfo(BaseModel):
    name: str
    work_year: float
    education_experience: list[str]
    work_experience: list[WorkExperience]


class CVModel(ORMBaseModel):
    title: str = Field(max_length=30)  # cv 的唯一标识
    basic_info: CVBasicInfo
    skills: list[str]
    project_experience: list[str]


class LLMCard(ORMBaseModel):
    """模型配置卡片"""
    model: str = Field(max_length=30)       # 模型名称 (API 调用规定的标准名称)
    is_local: bool                          # 是否是本地模型
    path: str = Field(max_length=50)        # 本地模型文件目录路径，或大模型 API base_url
    cost: float = Field(default=0.)         # 已使用大模型 API 费用（程序内计算）
    cost_limit: float = Field(default=1E8)  # 大模型 API 费用上限, 默认不设上限


# 面试官
class InterviewerModel(ORMBaseModel):
    """AI 面试官"""
    name: str = Field(max_length=20)
    model: str
    system_prompt: str


