from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os

# 直接导入model.py文件
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'service_end', 'data', 'model.py'))
print(f"Model file path: {model_path}")

if os.path.exists(model_path):
    # 动态导入模型
    import importlib.util
    spec = importlib.util.spec_from_file_location("model", model_path)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    WorkExperience = model.WorkExperience
    CVBasicInfo = model.CVBasicInfo
    CVModel = model.CVModel
    print("Successfully imported models from model.py")
else:
    print(f"Model file not found: {model_path}")
    # 如果导入失败，使用本地定义的模型
    class WorkExperience(BaseModel):
        """一个岗位的工作经历"""
        job: str = ""
        year: float = 0.0
        duty: str = ""  # 工作经历描述

    class CVBasicInfo(BaseModel):
        name: str = ""
        work_year: float = 0.0
        education_experience: list[str] = Field(default_factory=list)
        work_experience: list[WorkExperience] = Field(default_factory=list)

    class CVModel(BaseModel):
        title: str = Field(default="resume", max_length=30)  # cv 的唯一标识
        basic_info: CVBasicInfo = Field(default_factory=CVBasicInfo)
        skills: list[str] = Field(default_factory=list)
        project_experience: list[str] = Field(default_factory=list)
    print("Using local model definitions")


# 兼容旧模型，方便过渡
class PersonalInfo(BaseModel):
    """个人基本信息"""
    name: Optional[str] = Field(None, description="姓名")
    gender: Optional[str] = Field(None, description="性别")
    age: Optional[int] = Field(None, description="年龄")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    wechat: Optional[str] = Field(None, description="微信")
    github: Optional[str] = Field(None, description="GitHub")


class Education(BaseModel):
    """教育背景"""
    school: Optional[str] = Field(None, description="学校")
    major: Optional[str] = Field(None, description="专业")
    degree: Optional[str] = Field(None, description="学位")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    gpa: Optional[float] = Field(None, description="GPA")
    description: Optional[str] = Field(None, description="描述")


class OldWorkExperience(BaseModel):
    """工作经历"""
    company: Optional[str] = Field(None, description="公司名称")
    position: Optional[str] = Field(None, description="职位")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    description: Optional[str] = Field(None, description="工作描述")
    achievements: Optional[List[str]] = Field(default_factory=list, description="成就")


class ProjectExperience(BaseModel):
    """项目经验"""
    name: Optional[str] = Field(None, description="项目名称")
    role: Optional[str] = Field(None, description="角色")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    description: Optional[str] = Field(None, description="项目描述")
    technologies: Optional[List[str]] = Field(default_factory=list, description="技术栈")
    achievements: Optional[List[str]] = Field(default_factory=list, description="成就")


class Skill(BaseModel):
    """技能"""
    category: Optional[str] = Field(None, description="技能类别")
    items: Optional[List[str]] = Field(default_factory=list, description="技能项")


class Certificate(BaseModel):
    """证书"""
    name: Optional[str] = Field(None, description="证书名称")
    issuer: Optional[str] = Field(None, description="颁发机构")
    issue_date: Optional[str] = Field(None, description="获得时间")


class ResumeModel(BaseModel):
    """简历模型"""
    personal_info: Optional[PersonalInfo] = Field(default_factory=PersonalInfo, description="个人基本信息")
    education: Optional[List[Education]] = Field(default_factory=list, description="教育背景")
    work_experience: Optional[List[OldWorkExperience]] = Field(default_factory=list, description="工作经历")
    project_experience: Optional[List[ProjectExperience]] = Field(default_factory=list, description="项目经验")
    skills: Optional[List[Skill]] = Field(default_factory=list, description="技能")
    certificates: Optional[List[Certificate]] = Field(default_factory=list, description="证书")
    self_evaluation: Optional[str] = Field(None, description="自我评价")
    interests: Optional[List[str]] = Field(default_factory=list, description="兴趣爱好")

    class Config:
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "张三",
                    "gender": "男",
                    "age": 28,
                    "phone": "13800138000",
                    "email": "zhangsan@example.com",
                    "address": "北京市朝阳区"
                },
                "education": [
                    {
                        "school": "北京大学",
                        "major": "计算机科学与技术",
                        "degree": "硕士",
                        "start_date": "2018-09",
                        "end_date": "2021-06",
                        "gpa": 3.8
                    }
                ],
                "work_experience": [
                    {
                        "company": "ABC公司",
                        "position": "软件工程师",
                        "start_date": "2021-07",
                        "end_date": "2023-12",
                        "description": "负责后端开发工作"
                    }
                ],
                "skills": [
                    {
                        "category": "技术技能",
                        "items": ["Python", "Java", "C++"]
                    }
                ]
            }
        }
