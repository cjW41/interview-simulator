import pytest
from resume_extraction.src.extractor import ResumeExtractor


def test_extractor_initialization():
    """测试提取器初始化"""
    extractor = ResumeExtractor()
    assert extractor is not None


def test_detect_format():
    """测试格式检测"""
    extractor = ResumeExtractor()
    
    # 测试Markdown格式
    md_text = "# 张三\n## 个人信息\n电话：13800138000"
    assert extractor.detect_format(md_text) == 'markdown'
    
    # 测试文本格式
    txt_text = "张三\n电话：13800138000"
    assert extractor.detect_format(txt_text) == 'text'


def test_extract_from_text():
    """测试从文本提取"""
    extractor = ResumeExtractor()
    
    # 测试Markdown文本
    md_text = """# 张三
## 个人信息
电话：13800138000
邮箱：zhangsan@example.com

## 教育背景
北京大学
专业：计算机科学与技术
2018-09 至 2021-06

## 技能
技术技能：Python、Java、C++
"""
    
    resume = extractor.extract_from_text(md_text)
    assert resume is not None
    assert resume.personal_info.name == '张三'
    assert resume.personal_info.phone == '13800138000'
    assert resume.personal_info.email == 'zhangsan@example.com'
    assert len(resume.education) > 0
    assert len(resume.skills) > 0
    
    # 测试纯文本
    txt_text = """张三
电话：13800138000
邮箱：zhangsan@example.com

教育背景
北京大学
专业：计算机科学与技术
2018-09 至 2021-06

技能
技术技能：Python、Java、C++
"""
    
    resume = extractor.extract_from_text(txt_text)
    assert resume is not None
    assert resume.personal_info.name == '张三'
