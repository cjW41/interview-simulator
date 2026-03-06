from typing import Dict, List, Optional
from ..models import ResumeModel, PersonalInfo, Education, WorkExperience, ProjectExperience, Skill, Certificate


class ResumeValidator:
    """简历数据验证器"""
    
    def validate(self, resume: ResumeModel) -> Dict[str, List[str]]:
        """验证简历数据的完整性和准确性
        
        Args:
            resume: 简历模型
            
        Returns:
            Dict[str, List[str]]: 验证结果，键为验证类别，值为错误信息列表
        """
        errors = {}
        
        # 验证个人基本信息
        personal_info_errors = self._validate_personal_info(resume.personal_info)
        if personal_info_errors:
            errors['personal_info'] = personal_info_errors
        
        # 验证教育背景
        education_errors = self._validate_education(resume.education)
        if education_errors:
            errors['education'] = education_errors
        
        # 验证工作经历
        work_experience_errors = self._validate_work_experience(resume.work_experience)
        if work_experience_errors:
            errors['work_experience'] = work_experience_errors
        
        # 验证项目经验
        project_experience_errors = self._validate_project_experience(resume.project_experience)
        if project_experience_errors:
            errors['project_experience'] = project_experience_errors
        
        # 验证技能
        skills_errors = self._validate_skills(resume.skills)
        if skills_errors:
            errors['skills'] = skills_errors
        
        # 验证证书
        certificates_errors = self._validate_certificates(resume.certificates)
        if certificates_errors:
            errors['certificates'] = certificates_errors
        
        return errors
    
    def _validate_personal_info(self, personal_info: PersonalInfo) -> List[str]:
        """验证个人基本信息"""
        errors = []
        
        if not personal_info.name:
            errors.append('姓名不能为空')
        
        if not personal_info.phone and not personal_info.email:
            errors.append('至少需要提供电话或邮箱')
        
        return errors
    
    def _validate_education(self, education_list: List[Education]) -> List[str]:
        """验证教育背景"""
        errors = []
        
        if not education_list:
            errors.append('教育背景不能为空')
        else:
            for i, education in enumerate(education_list):
                if not education.school:
                    errors.append(f'第{i+1}条教育记录的学校不能为空')
                if not education.major:
                    errors.append(f'第{i+1}条教育记录的专业不能为空')
                if not education.start_date or not education.end_date:
                    errors.append(f'第{i+1}条教育记录的时间范围不能为空')
        
        return errors
    
    def _validate_work_experience(self, work_list: List[WorkExperience]) -> List[str]:
        """验证工作经历"""
        errors = []
        
        for i, work in enumerate(work_list):
            if not work.company:
                errors.append(f'第{i+1}条工作经历的公司名称不能为空')
            if not work.position:
                errors.append(f'第{i+1}条工作经历的职位不能为空')
            if not work.start_date or not work.end_date:
                errors.append(f'第{i+1}条工作经历的时间范围不能为空')
        
        return errors
    
    def _validate_project_experience(self, project_list: List[ProjectExperience]) -> List[str]:
        """验证项目经验"""
        errors = []
        
        for i, project in enumerate(project_list):
            if not project.name:
                errors.append(f'第{i+1}个项目的名称不能为空')
            if not project.description:
                errors.append(f'第{i+1}个项目的描述不能为空')
        
        return errors
    
    def _validate_skills(self, skills_list: List[Skill]) -> List[str]:
        """验证技能"""
        errors = []
        
        if not skills_list:
            errors.append('技能列表不能为空')
        else:
            for i, skill in enumerate(skills_list):
                if not skill.items:
                    errors.append(f'第{i+1}类技能的内容不能为空')
        
        return errors
    
    def _validate_certificates(self, cert_list: List[Certificate]) -> List[str]:
        """验证证书"""
        errors = []
        
        for i, cert in enumerate(cert_list):
            if not cert.name:
                errors.append(f'第{i+1}个证书的名称不能为空')
        
        return errors
    
    def get_data_quality_score(self, resume: ResumeModel) -> float:
        """计算简历数据质量评分
        
        Args:
            resume: 简历模型
            
        Returns:
            float: 质量评分（0-100）
        """
        total_score = 0
        max_score = 0
        
        # 个人基本信息评分（30分）
        personal_score = 0
        if resume.personal_info.name:
            personal_score += 10
        if resume.personal_info.phone or resume.personal_info.email:
            personal_score += 10
        if resume.personal_info.address:
            personal_score += 5
        if resume.personal_info.wechat or resume.personal_info.github:
            personal_score += 5
        total_score += personal_score
        max_score += 30
        
        # 教育背景评分（20分）
        education_score = 0
        if resume.education:
            education_score += 10
            for edu in resume.education:
                if edu.school and edu.major:
                    education_score += 5
                    break
        total_score += education_score
        max_score += 20
        
        # 工作经历评分（20分）
        work_score = 0
        if resume.work_experience:
            work_score += 10
            for work in resume.work_experience:
                if work.company and work.position:
                    work_score += 10
                    break
        total_score += work_score
        max_score += 20
        
        # 项目经验评分（15分）
        project_score = 0
        if resume.project_experience:
            project_score += 15
        total_score += project_score
        max_score += 15
        
        # 技能评分（10分）
        skill_score = 0
        if resume.skills:
            skill_score += 10
        total_score += skill_score
        max_score += 10
        
        # 证书评分（5分）
        cert_score = 0
        if resume.certificates:
            cert_score += 5
        total_score += cert_score
        max_score += 5
        
        if max_score == 0:
            return 0
        
        return (total_score / max_score) * 100
