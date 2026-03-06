import os
from typing import Optional, Dict, Any
from .models import ResumeModel, CVModel, CVBasicInfo, WorkExperience
from .parsers import MarkdownParser, TextParser, PdfParser
from .utils.llm_client import LLMClient


class ResumeExtractor:
    """简历结构化提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.md_parser = MarkdownParser()
        self.txt_parser = TextParser()
        self.pdf_parser = PdfParser()
        self.llm_client = LLMClient()
    
    def extract_from_file(self, file_path: str) -> ResumeModel:
        """从文件中提取简历信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            ResumeModel: 解析后的简历模型
        """
        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        # 读取文件内容
        if ext == '.pdf':
            # 解析PDF文件
            text = self.pdf_parser.extract_text(file_path)
        else:
            # 读取文本文件
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # 使用大模型提取信息
        return self.extract_from_text(text)
    
    def extract_from_text(self, text: str) -> ResumeModel:
        """从文本内容中提取简历信息
        
        Args:
            text: 简历文本内容
            
        Returns:
            ResumeModel: 解析后的简历模型
        """
        # 使用大模型提取信息
        llm_result = self.llm_client.extract_resume_info(text)
        
        # 转换为ResumeModel
        return self._convert_llm_result_to_resume_model(llm_result)
    
    def _convert_llm_result_to_resume_model(self, llm_result: Dict[str, Any]) -> ResumeModel:
        """将大模型返回的结果转换为ResumeModel
        
        Args:
            llm_result: 大模型返回的结果
            
        Returns:
            ResumeModel: 转换后的简历模型
        """
        from .models import PersonalInfo, Education, OldWorkExperience as WorkExperience, ProjectExperience, Skill, Certificate
        
        # 创建个人信息
        personal_info = PersonalInfo(
            name=llm_result.get('name'),
            gender=llm_result.get('gender'),
            age=llm_result.get('age'),
            phone=llm_result.get('phone'),
            email=llm_result.get('email'),
            address=llm_result.get('address')
        )
        
        # 创建教育背景
        education = []
        for edu in llm_result.get('education', []):
            education.append(Education(
                school=edu.get('school'),
                major=edu.get('major'),
                degree=edu.get('degree'),
                start_date=edu.get('start_date'),
                end_date=edu.get('end_date'),
                gpa=edu.get('gpa')
            ))
        
        # 创建工作经历
        work_experience = []
        for work in llm_result.get('work_experience', []):
            work_experience.append(WorkExperience(
                company=work.get('company'),
                position=work.get('position'),
                start_date=work.get('start_date'),
                end_date=work.get('end_date'),
                description=work.get('description')
            ))
        
        # 创建项目经验
        project_experience = []
        for project in llm_result.get('project_experience', []):
            project_experience.append(ProjectExperience(
                name=project.get('name'),
                role=project.get('role'),
                start_date=project.get('start_date'),
                end_date=project.get('end_date'),
                description=project.get('description'),
                technologies=project.get('technologies', [])
            ))
        
        # 创建技能
        skills = []
        for skill in llm_result.get('skills', []):
            skills.append(Skill(
                category=skill.get('category'),
                items=skill.get('items', [])
            ))
        
        # 创建证书
        certificates = []
        for cert_name in llm_result.get('certificates', []):
            certificates.append(Certificate(name=cert_name))
        
        # 创建简历模型
        resume = ResumeModel(
            personal_info=personal_info,
            education=education,
            work_experience=work_experience,
            project_experience=project_experience,
            skills=skills,
            certificates=certificates,
            self_evaluation=llm_result.get('self_evaluation'),
            interests=llm_result.get('interests', [])
        )
        
        return resume
    
    def detect_format(self, text: str) -> str:
        """检测文本格式
        
        Args:
            text: 文本内容
            
        Returns:
            str: 格式类型 ('markdown', 'text', 'unknown')
        """
        if '#' in text or '##' in text:
            return 'markdown'
        else:
            return 'text'
    
    def to_cv_model(self, resume: ResumeModel, title: str = "resume") -> CVModel:
        """将ResumeModel转换为CVModel格式
        
        Args:
            resume: 解析后的简历模型
            title: CV的唯一标识
            
        Returns:
            CVModel: 符合service_end/data/model.py格式的简历模型
        """
        # 计算工作年限
        work_year = self._calculate_work_year(resume)
        
        # 构建教育经历列表
        education_experience = []
        for edu in resume.education:
            edu_str = f"{edu.school} - {edu.major} ({edu.degree})"
            if edu.start_date and edu.end_date:
                edu_str += f" {edu.start_date} 至 {edu.end_date}"
            education_experience.append(edu_str)
        
        # 构建工作经历列表
        work_experience = []
        for work in resume.work_experience:
            if work.company and work.position:
                job = f"{work.company} - {work.position}"
                duty = work.description or ""
                # 计算该工作的年限
                job_year = self._calculate_job_year(work.start_date, work.end_date)
                work_experience.append(WorkExperience(
                    job=job,
                    year=job_year,
                    duty=duty
                ))
        
        # 构建技能列表
        skills = []
        for skill in resume.skills:
            if skill.items:
                skills.extend(skill.items)
        
        # 构建项目经验列表
        project_experience = []
        for project in resume.project_experience:
            project_str = f"{project.name}"
            if project.role:
                project_str += f" - {project.role}"
            if project.description:
                project_str += f": {project.description}"
            if project.technologies:
                project_str += f" 技术栈: {', '.join(project.technologies)}"
            project_experience.append(project_str)
        
        # 构建CVBasicInfo
        basic_info = CVBasicInfo(
            name=resume.personal_info.name or "",
            work_year=work_year,
            education_experience=education_experience,
            work_experience=work_experience
        )
        
        # 构建CVModel
        cv_model = CVModel(
            title=title,
            basic_info=basic_info,
            skills=skills,
            project_experience=project_experience
        )
        
        return cv_model
    
    def _calculate_work_year(self, resume: ResumeModel) -> float:
        """计算总工作年限
        
        Args:
            resume: 解析后的简历模型
            
        Returns:
            float: 总工作年限
        """
        total_years = 0.0
        for work in resume.work_experience:
            years = self._calculate_job_year(work.start_date, work.end_date)
            total_years += years
        return total_years
    
    def _calculate_job_year(self, start_date: Optional[str], end_date: Optional[str]) -> float:
        """计算单个工作的年限
        
        Args:
            start_date: 开始时间
            end_date: 结束时间
            
        Returns:
            float: 工作年限
        """
        if not start_date or not end_date:
            return 0.0
        
        try:
            # 简单计算：假设格式为 YYYY-MM
            start_parts = start_date.split('-')
            end_parts = end_date.split('-')
            
            if len(start_parts) >= 2 and len(end_parts) >= 2:
                start_year = int(start_parts[0])
                start_month = int(start_parts[1])
                end_year = int(end_parts[0])
                end_month = int(end_parts[1])
                
                years = (end_year - start_year) + (end_month - start_month) / 12
                return max(0.0, years)
        except:
            pass
        
        return 0.0
