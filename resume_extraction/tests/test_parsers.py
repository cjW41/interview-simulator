import pytest
from resume_extraction.src.parsers import MarkdownParser, TextParser


def test_markdown_parser():
    """测试Markdown解析器"""
    parser = MarkdownParser()
    
    md_text = """# 张三
## 个人信息
电话：13800138000
邮箱：zhangsan@example.com

## 教育背景
北京大学
专业：计算机科学与技术
2018-09 至 2021-06

## 工作经历
ABC公司
职位：软件工程师
2021-07 至 2023-12
负责后端开发工作

## 技能
技术技能：Python、Java、C++
"""
    
    resume = parser.parse(md_text)
    assert resume is not None
    assert resume.personal_info.name == '张三'
    assert resume.personal_info.phone == '13800138000'
    assert resume.personal_info.email == 'zhangsan@example.com'
    assert len(resume.education) > 0
    assert len(resume.work_experience) > 0
    assert len(resume.skills) > 0


def test_text_parser():
    """测试文本解析器"""
    parser = TextParser()
    
    txt_text = """张三
电话：13800138000
邮箱：zhangsan@example.com

教育背景
北京大学
专业：计算机科学与技术
2018-09 至 2021-06

工作经历
ABC公司
职位：软件工程师
2021-07 至 2023-12
负责后端开发工作

技能
技术技能：Python、Java、C++
"""
    
    resume = parser.parse(txt_text)
    assert resume is not None
    assert resume.personal_info.name == '张三'
    assert resume.personal_info.phone == '13800138000'
    assert resume.personal_info.email == 'zhangsan@example.com'
    assert len(resume.education) > 0
    assert len(resume.work_experience) > 0
    assert len(resume.skills) > 0
