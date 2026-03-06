import re
from typing import Dict, Optional, List
from ..models import ResumeModel, PersonalInfo, Education, WorkExperience, ProjectExperience, Skill, Certificate
from ..utils.text_utils import (
    extract_email, extract_phone, extract_wechat, extract_github,
    extract_dates, extract_gpa, clean_text, split_by_section
)


class TextParser:
    """纯文本格式简历解析器"""
    
    def parse(self, text: str) -> ResumeModel:
        """解析纯文本格式的简历文本"""
        # 清理文本
        text = clean_text(text)
        
        # 初始化简历模型
        resume = ResumeModel()
        
        # 提取个人基本信息
        resume.personal_info = self._extract_personal_info(text)
        
        # 提取教育背景
        resume.education = self._extract_education(text)
        
        # 提取工作经历
        resume.work_experience = self._extract_work_experience(text)
        
        # 提取项目经验
        resume.project_experience = self._extract_project_experience(text)
        
        # 提取技能
        resume.skills = self._extract_skills(text)
        
        # 提取证书
        resume.certificates = self._extract_certificates(text)
        
        # 提取自我评价
        resume.self_evaluation = self._extract_self_evaluation(text)
        
        # 提取兴趣爱好
        resume.interests = self._extract_interests(text)
        
        return resume
    
    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """提取个人基本信息"""
        personal_info = PersonalInfo()
        
        # 提取姓名（通常在文档开头）
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line for keyword in ['联系方式', '教育背景', '工作经历', '项目经验', '技能', '证书', '自我评价', '兴趣爱好']):
                personal_info.name = line
                break
        
        # 提取联系方式
        personal_info.email = extract_email(text)
        personal_info.phone = extract_phone(text)
        personal_info.wechat = extract_wechat(text)
        personal_info.github = extract_github(text)
        
        # 提取性别和年龄
        if '男' in text:
            personal_info.gender = '男'
        elif '女' in text:
            personal_info.gender = '女'
        
        # 提取年龄
        age_match = re.search(r'(\d+)岁', text)
        if age_match:
            personal_info.age = int(age_match.group(1))
        
        # 提取地址
        address_match = re.search(r'地址[:：]?\s*(.+)', text)
        if address_match:
            personal_info.address = address_match.group(1)
        
        return personal_info
    
    def _extract_education(self, text: str) -> List[Education]:
        """提取教育背景"""
        education_list = []
        
        # 查找教育相关章节
        sections = ['教育背景', '教育经历', 'education']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按段落分割
            paragraphs = section_text.split('\n\n')
            for para in paragraphs:
                if para:
                    education = Education()
                    
                    # 提取学校
                    school_match = re.search(r'([^\n]+)', para)
                    if school_match:
                        education.school = school_match.group(1)
                    
                    # 提取专业
                    major_match = re.search(r'专业[:：]?\s*(.+)', para)
                    if major_match:
                        education.major = major_match.group(1)
                    
                    # 提取学位
                    degree_match = re.search(r'学位[:：]?\s*(.+)', para)
                    if degree_match:
                        education.degree = degree_match.group(1)
                    
                    # 提取日期
                    dates = extract_dates(para)
                    if len(dates) >= 2:
                        education.start_date = dates[0]
                        education.end_date = dates[1]
                    
                    # 提取GPA
                    education.gpa = extract_gpa(para)
                    
                    # 提取描述
                    education.description = para
                    
                    education_list.append(education)
        
        return education_list
    
    def _extract_work_experience(self, text: str) -> List[WorkExperience]:
        """提取工作经历"""
        work_list = []
        
        # 查找工作经历相关章节
        sections = ['工作经历', '职业经历', 'work experience']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按段落分割
            paragraphs = section_text.split('\n\n')
            for para in paragraphs:
                if para:
                    work = WorkExperience()
                    
                    # 提取公司名称
                    company_match = re.search(r'([^\n]+)', para)
                    if company_match:
                        work.company = company_match.group(1)
                    
                    # 提取职位
                    position_match = re.search(r'职位[:：]?\s*(.+)', para)
                    if position_match:
                        work.position = position_match.group(1)
                    
                    # 提取日期
                    dates = extract_dates(para)
                    if len(dates) >= 2:
                        work.start_date = dates[0]
                        work.end_date = dates[1]
                    
                    # 提取工作描述
                    work.description = para
                    
                    work_list.append(work)
        
        return work_list
    
    def _extract_project_experience(self, text: str) -> List[ProjectExperience]:
        """提取项目经验"""
        project_list = []
        
        # 查找项目经验相关章节
        sections = ['项目经验', '项目经历', 'projects']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按段落分割
            paragraphs = section_text.split('\n\n')
            for para in paragraphs:
                if para:
                    project = ProjectExperience()
                    
                    # 提取项目名称
                    project_match = re.search(r'([^\n]+)', para)
                    if project_match:
                        project.name = project_match.group(1)
                    
                    # 提取角色
                    role_match = re.search(r'角色[:：]?\s*(.+)', para)
                    if role_match:
                        project.role = role_match.group(1)
                    
                    # 提取日期
                    dates = extract_dates(para)
                    if len(dates) >= 2:
                        project.start_date = dates[0]
                        project.end_date = dates[1]
                    
                    # 提取项目描述
                    project.description = para
                    
                    # 提取技术栈
                    tech_match = re.search(r'技术栈[:：]?\s*(.+)', para)
                    if tech_match:
                        project.technologies = [tech.strip() for tech in tech_match.group(1).split('、')]
                    
                    project_list.append(project)
        
        return project_list
    
    def _extract_skills(self, text: str) -> List[Skill]:
        """提取技能"""
        skills_list = []
        
        # 查找技能相关章节
        sections = ['技能', '专业技能', 'skills']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按行分割
            lines = section_text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # 检查是否是技能类别
                    if ':' in line or '：' in line:
                        if ':' in line:
                            category, items = line.split(':', 1)
                        else:
                            category, items = line.split('：', 1)
                        category = category.strip()
                        items = [item.strip() for item in items.split('、')]
                        skills_list.append(Skill(category=category, items=items))
                    else:
                        # 简单的技能列表
                        items = [item.strip() for item in line.split('、')]
                        skills_list.append(Skill(category='技能', items=items))
        
        return skills_list
    
    def _extract_certificates(self, text: str) -> List[Certificate]:
        """提取证书"""
        cert_list = []
        
        # 查找证书相关章节
        sections = ['证书', '资质证书', 'certificates']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按行分割
            lines = section_text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    cert = Certificate()
                    cert.name = line
                    # 简单处理，实际项目中可能需要更复杂的解析
                    cert_list.append(cert)
        
        return cert_list
    
    def _extract_self_evaluation(self, text: str) -> Optional[str]:
        """提取自我评价"""
        sections = ['自我评价', '个人评价', 'self evaluation']
        return self._find_section(text, sections)
    
    def _extract_interests(self, text: str) -> List[str]:
        """提取兴趣爱好"""
        sections = ['兴趣爱好', '爱好', 'interests']
        section_text = self._find_section(text, sections)
        if section_text:
            return [item.strip() for item in section_text.split('、')]
        return []
    
    def _find_section(self, text: str, section_names: List[str]) -> Optional[str]:
        """查找指定章节的内容"""
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            line = line.strip()
            # 检查是否是章节标题
            is_section_title = False
            for section_name in section_names:
                if re.search(rf'^{section_name}$', line, re.IGNORECASE):
                    is_section_title = True
                    break
            
            if is_section_title:
                in_section = True
                continue
            
            # 检查是否是下一个章节标题
            if in_section and line and any(re.search(rf'^{name}$', line, re.IGNORECASE) for name in ['教育背景', '工作经历', '项目经验', '技能', '证书', '自我评价', '兴趣爱好']):
                break
            
            if in_section and line:
                section_content.append(line)
        
        if section_content:
            return '\n'.join(section_content)
        return None
