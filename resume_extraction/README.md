# 简历结构化提取智能体

## 项目概述

本项目实现了一个简历结构化提取智能体，能够从各种格式的简历中提取结构化信息，包括个人基本信息、教育背景、工作经历、技能等。

## 目录结构

```
resume_extraction/
├── README.md              # 项目说明
├── requirements.txt       # 依赖项
├── implementation_guide.md # 实现指南
├── src/
│   ├── __init__.py
│   ├── extractor.py       # 核心提取器
│   ├── models.py          # 数据模型
│   ├── parsers/           # 不同格式解析器
│   │   ├── __init__.py
│   │   ├── md_parser.py   # Markdown解析器
│   │   ├── txt_parser.py  # 文本解析器
│   │   └── pdf_parser.py  # PDF解析器
│   ├── utils/             # 工具函数
│   │   ├── __init__.py
│   │   └── text_utils.py  # 文本处理工具
│   └── validators/        # 验证器
│       ├── __init__.py
│       └── validator.py   # 数据验证
├── tests/                 # 测试目录
│   ├── __init__.py
│   ├── test_extractor.py  # 提取器测试
│   └── test_parsers.py    # 解析器测试
└── examples/              # 示例
    └── test_resume.md     # 测试简历
```

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装项目

```bash
pip install -e .
```

## 使用方法

### 基本用法

```python
from resume_extraction.src.extractor import ResumeExtractor

# 从文件路径提取
extractor = ResumeExtractor()
resume_data = extractor.extract_from_file('path/to/resume.md')

# 从文本内容提取
resume_text = """# 张三
## 个人信息
..."""
resume_data = extractor.extract_from_text(resume_text)

print(resume_data)
```

### 示例

查看 `examples` 目录中的示例简历和使用示例。

## 支持的格式

- Markdown (.md)
- 纯文本 (.txt)
- PDF (.pdf) [可选，需要安装 PyPDF2]

## 提取的信息

- **个人基本信息**：姓名、性别、年龄、联系方式、地址
- **教育背景**：学校、专业、学位、毕业时间、GPA
- **工作经历**：公司名称、职位、工作时间、工作描述
- **项目经验**：项目名称、角色、项目时间、项目描述、技术栈
- **技能**：技术技能、语言技能、软技能
- **证书**：证书名称、颁发机构、获得时间
- **其他信息**：自我评价、兴趣爱好等

## 测试

运行测试：

```bash
pytest tests/
```

## 集成

本项目可以作为独立模块集成到其他系统中，也可以通过API接口提供服务。

## 未来计划

- 支持更多简历格式
- 集成机器学习模型提高提取准确性
- 支持多语言简历
- 提供Web接口
