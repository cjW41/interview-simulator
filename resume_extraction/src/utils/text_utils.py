import re
import regex
from typing import List, Optional


def clean_text(text: str) -> str:
    """清理文本，去除多余的空白字符"""
    # 按行处理，保留换行符和缩进
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # 保留行首缩进
        indent = len(line) - len(line.lstrip())
        # 去除行内多余的空白字符
        line_content = re.sub(r'\s+', ' ', line.strip())
        # 重新添加缩进
        cleaned_line = ' ' * indent + line_content
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)
    # 重新组合成文本
    return '\n'.join(cleaned_lines)


def extract_email(text: str) -> Optional[str]:
    """从文本中提取邮箱地址"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """从文本中提取电话号码"""
    # 匹配中国大陆手机号
    pattern = r'1[3-9]\d{9}'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    # 匹配固定电话
    pattern = r'\d{3,4}-?\d{7,8}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_wechat(text: str) -> Optional[str]:
    """从文本中提取微信号"""
    # 简单匹配微信号格式
    pattern = r'微信[:：]?\s*([a-zA-Z0-9_-]{6,20})'
    match = re.search(pattern, text)
    return match.group(1) if match else None


def extract_github(text: str) -> Optional[str]:
    """从文本中提取GitHub地址"""
    # 忽略大小写匹配
    pattern = r'github[:：]?\s*(https?://github\.com/[a-zA-Z0-9_-]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    # 匹配GitHub用户名
    pattern = r'github[:：]?\s*@?([a-zA-Z0-9_-]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return f"https://github.com/{match.group(1)}"
    return None


def extract_dates(text: str) -> List[str]:
    """从文本中提取日期"""
    # 匹配YYYY-MM-DD格式
    pattern = r'\d{4}-\d{2}-\d{2}'
    matches = re.findall(pattern, text)
    if matches:
        return matches
    # 匹配YYYY/MM/DD格式
    pattern = r'\d{4}/\d{2}/\d{2}'
    matches = re.findall(pattern, text)
    if matches:
        return matches
    # 匹配YYYY年MM月格式
    pattern = r'\d{4}年\d{1,2}月'
    matches = re.findall(pattern, text)
    return matches


def extract_gpa(text: str) -> Optional[float]:
    """从文本中提取GPA"""
    pattern = r'GPA[:：]?\s*([0-9]+(\.[0-9]+)?)'
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


def split_by_section(text: str, sections: List[str]) -> dict:
    """根据章节标题分割文本"""
    result = {}
    current_section = None
    current_content = []
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检查是否是章节标题
        section_match = None
        for section in sections:
            if re.search(rf'^{section}$', line, re.IGNORECASE):
                section_match = section
                break
        
        if section_match:
            # 保存当前章节内容
            if current_section:
                result[current_section] = '\n'.join(current_content)
            # 开始新章节
            current_section = section_match
            current_content = []
        elif current_section:
            current_content.append(line)
    
    # 保存最后一个章节
    if current_section:
        result[current_section] = '\n'.join(current_content)
    
    return result


def normalize_text(text: str) -> str:
    """标准化文本"""
    # 转换为小写
    text = text.lower()
    # 去除特殊字符
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    return text


def extract_skills(text: str) -> List[str]:
    """从文本中提取技能列表"""
    # 简单的技能提取，实际项目中可能需要更复杂的规则
    # 这里只是一个示例
    skills = []
    # 常见的技术技能关键词
    tech_keywords = [
        'python', 'java', 'c++', 'javascript', 'react', 'vue', 'angular',
        'node.js', 'spring', 'django', 'flask', 'mysql', 'postgresql', 'mongodb',
        'redis', 'docker', 'kubernetes', 'aws', 'azure', 'git', 'linux'
    ]
    
    text = normalize_text(text)
    for keyword in tech_keywords:
        if keyword in text:
            skills.append(keyword)
    
    return skills
