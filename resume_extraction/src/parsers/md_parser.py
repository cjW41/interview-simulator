import re
from typing import Dict, Optional, List
from ..models import ResumeModel, PersonalInfo, Education, OldWorkExperience as WorkExperience, ProjectExperience, Skill, Certificate
from ..utils.text_utils import (
    extract_email, extract_phone, extract_wechat, extract_github,
    extract_dates, extract_gpa, clean_text, split_by_section
)


class MarkdownParser:
    """Markdown格式简历解析器"""
    
    def parse(self, text: str) -> ResumeModel:
        """解析Markdown格式的简历文本"""
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
        
        # 提取姓名（通常在文档开头，可能是# 姓名格式）
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # 移除Markdown标记后获取姓名
                if line.startswith('#'):
                    # 移除#和空格
                    name = line.lstrip('#').strip()
                    if name:
                        personal_info.name = name
                        break
                else:
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
            # 按列表项分割
            lines = section_text.split('\n')
            current_edu = None
            
            for line in lines:
                line = line.rstrip()  # 只去除右侧空白，保留缩进
                # 计算缩进级别（2个空格为一级）
                indent_level = len(line) - len(line.lstrip())
                
                if line.strip().startswith('- '):
                    if indent_level == 0:
                        # 新的教育条目（一级列表项）
                        if current_edu:
                            education_list.append(current_edu)
                        current_edu = Education()
                        # 提取学校名称，去除开头的'- '
                        school_name = line.strip()[2:].strip()
                        current_edu.school = school_name
                    elif current_edu and indent_level >= 2:
                        # 教育条目的详细信息（二级列表项）
                        detail_line = line.strip()[2:].strip()
                        if '专业：' in detail_line or '专业:' in detail_line:
                            if '专业：' in detail_line:
                                _, major = detail_line.split('专业：', 1)
                            else:
                                _, major = detail_line.split('专业:', 1)
                            current_edu.major = major.strip()
                        elif '学位：' in detail_line or '学位:' in detail_line:
                            if '学位：' in detail_line:
                                _, degree = detail_line.split('学位：', 1)
                            else:
                                _, degree = detail_line.split('学位:', 1)
                            current_edu.degree = degree.strip()
                        elif '时间：' in detail_line or '时间:' in detail_line:
                            if '时间：' in detail_line:
                                _, time_range = detail_line.split('时间：', 1)
                            else:
                                _, time_range = detail_line.split('时间:', 1)
                            time_range = time_range.strip()
                            if '至' in time_range:
                                start_date, end_date = time_range.split('至', 1)
                                current_edu.start_date = start_date.strip()
                                current_edu.end_date = end_date.strip()
                        elif 'GPA：' in detail_line or 'GPA:' in detail_line:
                            if 'GPA：' in detail_line:
                                _, gpa = detail_line.split('GPA：', 1)
                            else:
                                _, gpa = detail_line.split('GPA:', 1)
                            try:
                                current_edu.gpa = float(gpa.strip())
                            except ValueError:
                                pass
            
            # 添加最后一个教育条目
            if current_edu:
                education_list.append(current_edu)
        
        return education_list
    
    def _extract_work_experience(self, text: str) -> List[WorkExperience]:
        """提取工作经历"""
        work_list = []
        
        # 查找工作经历相关章节
        sections = ['工作经历', '职业经历', 'work experience']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按列表项分割
            lines = section_text.split('\n')
            current_work = None
            
            for line in lines:
                line = line.rstrip()  # 只去除右侧空白，保留缩进
                # 计算缩进级别（2个空格为一级）
                indent_level = len(line) - len(line.lstrip())
                
                if line.strip().startswith('- '):
                    if indent_level == 0:
                        # 新的工作条目（一级列表项）
                        if current_work:
                            work_list.append(current_work)
                        current_work = WorkExperience()
                        # 提取公司名称，去除开头的'- '
                        company_name = line.strip()[2:].strip()
                        current_work.company = company_name
                    elif current_work and indent_level >= 2:
                        # 工作条目的详细信息（二级列表项）
                        detail_line = line.strip()[2:].strip()
                        if '职位：' in detail_line or '职位:' in detail_line:
                            if '职位：' in detail_line:
                                _, position = detail_line.split('职位：', 1)
                            else:
                                _, position = detail_line.split('职位:', 1)
                            current_work.position = position.strip()
                        elif '时间：' in detail_line or '时间:' in detail_line:
                            if '时间：' in detail_line:
                                _, time_range = detail_line.split('时间：', 1)
                            else:
                                _, time_range = detail_line.split('时间:', 1)
                            time_range = time_range.strip()
                            if '至' in time_range:
                                start_date, end_date = time_range.split('至', 1)
                                current_work.start_date = start_date.strip()
                                current_work.end_date = end_date.strip()
                        elif '工作描述：' in detail_line or '工作描述:' in detail_line:
                            if '工作描述：' in detail_line:
                                _, description = detail_line.split('工作描述：', 1)
                            else:
                                _, description = detail_line.split('工作描述:', 1)
                            current_work.description = description.strip()
                        elif '主要成就：' in detail_line or '主要成就:' in detail_line:
                            # 跳过主要成就标题，后续行会处理
                            pass
                        else:
                            # 处理主要成就内容或其他详细信息
                            if current_work.description:
                                current_work.description += ' ' + detail_line
                            else:
                                current_work.description = detail_line
            
            # 添加最后一个工作条目
            if current_work:
                work_list.append(current_work)
        
        return work_list
    
    def _extract_project_experience(self, text: str) -> List[ProjectExperience]:
        """提取项目经验"""
        project_list = []
        
        # 查找项目经验相关章节
        sections = ['项目经验', '项目经历', 'projects']
        section_text = self._find_section(text, sections)
        
        if section_text:
            # 按列表项分割
            lines = section_text.split('\n')
            current_project = None
            
            for line in lines:
                line = line.rstrip()  # 只去除右侧空白，保留缩进
                # 计算缩进级别（2个空格为一级）
                indent_level = len(line) - len(line.lstrip())
                
                if line.strip().startswith('- '):
                    if indent_level == 0:
                        # 新的项目条目（一级列表项）
                        if current_project:
                            project_list.append(current_project)
                        current_project = ProjectExperience()
                        # 提取项目名称，去除开头的'- '
                        project_name = line.strip()[2:].strip()
                        current_project.name = project_name
                    elif current_project and indent_level >= 2:
                        # 项目条目的详细信息（二级列表项）
                        detail_line = line.strip()[2:].strip()
                        if '角色：' in detail_line or '角色:' in detail_line:
                            if '角色：' in detail_line:
                                _, role = detail_line.split('角色：', 1)
                            else:
                                _, role = detail_line.split('角色:', 1)
                            current_project.role = role.strip()
                        elif '时间：' in detail_line or '时间:' in detail_line:
                            if '时间：' in detail_line:
                                _, time_range = detail_line.split('时间：', 1)
                            else:
                                _, time_range = detail_line.split('时间:', 1)
                            time_range = time_range.strip()
                            if '至' in time_range:
                                start_date, end_date = time_range.split('至', 1)
                                current_project.start_date = start_date.strip()
                                current_project.end_date = end_date.strip()
                        elif '项目描述：' in detail_line or '项目描述:' in detail_line:
                            if '项目描述：' in detail_line:
                                _, description = detail_line.split('项目描述：', 1)
                            else:
                                _, description = detail_line.split('项目描述:', 1)
                            current_project.description = description.strip()
                        elif '技术栈：' in detail_line or '技术栈:' in detail_line:
                            if '技术栈：' in detail_line:
                                _, tech = detail_line.split('技术栈：', 1)
                            else:
                                _, tech = detail_line.split('技术栈:', 1)
                            current_project.technologies = [t.strip() for t in tech.split('、')]
                        elif '主要成就：' in detail_line or '主要成就:' in detail_line:
                            # 跳过主要成就标题，后续行会处理
                            pass
                        else:
                            # 处理主要成就内容或其他详细信息
                            if current_project.description:
                                current_project.description += ' ' + detail_line
                            else:
                                current_project.description = detail_line
            
            # 添加最后一个项目条目
            if current_project:
                project_list.append(current_project)
        
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
                line = line.rstrip()  # 只去除右侧空白，保留缩进
                if line.startswith('- '):
                    # 处理列表形式的技能（一级列表项）
                    skill_line = line[2:].strip()
                    if ':' in skill_line or '：' in skill_line:
                        if ':' in skill_line:
                            category, items = skill_line.split(':', 1)
                        else:
                            category, items = skill_line.split('：', 1)
                        category = category.strip()
                        # 提取技能项目，保留熟练程度信息
                        items = [item.strip() for item in items.split('、')]
                        skills_list.append(Skill(category=category, items=items))
                    else:
                        # 简单的技能列表
                        items = [item.strip() for item in skill_line.split('、')]
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
                line = line.rstrip()  # 只去除右侧空白，保留缩进
                if line.startswith('- '):
                    # 处理列表形式的证书（一级列表项）
                    cert_name = line[2:].strip()
                    if cert_name:
                        cert = Certificate()
                        cert.name = cert_name
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
            # 保留原始行（包括缩进）
            original_line = line
            # 处理后的行用于检测标题
            stripped_line = line.strip()
            # 移除Markdown标记，获取纯文本标题
            clean_line = stripped_line.lstrip('#').strip()
            
            # 检查是否是章节标题
            is_section_title = False
            for section_name in section_names:
                if re.search(rf'^{section_name}$', clean_line, re.IGNORECASE):
                    is_section_title = True
                    break
            
            if is_section_title:
                in_section = True
                continue
            
            # 检查是否是下一个章节标题
            if in_section and stripped_line and (stripped_line.startswith('#') or any(re.search(rf'^{name}$', clean_line, re.IGNORECASE) for name in ['教育背景', '工作经历', '项目经验', '技能', '证书', '自我评价', '兴趣爱好'])):
                break
            
            if in_section and original_line:
                section_content.append(original_line)
        
        if section_content:
            return '\n'.join(section_content)
        return None
