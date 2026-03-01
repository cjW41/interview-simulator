from ..data.model import CVModel, CVBasicInfo, WorkExperience


async def parse_cv_workflow(cv_str: str, title: str) -> CVModel:
    """解析用户上传 CV (待实现)"""
    # 用于测试
    return CVModel(
        title=title,
        basic_info=CVBasicInfo(
            name="Alice",
            work_year=3.5,
            education_experience=["college"],
            work_experience=[
                WorkExperience(
                    job="machine learning",
                    year=1.,
                    duty="finance data analyze"
                )
            ]
        ),
        skills=["skill1", "skill2"],
        project_experience=["project1", "project2"]
    )


