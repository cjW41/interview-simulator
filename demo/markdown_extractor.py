import gradio as gr
import os
import re
import json
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import dashscope
from dashscope import Generation
import pdfplumber

load_dotenv()
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

def extract_markdown_content(file):
    if file is None:
        return "", None
    
    try:
        file_path = file.name
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            content = pdf_to_markdown(file_path)
        elif file_ext in ['.md', '.markdown']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            return "错误: 请上传.md、.markdown或.pdf格式的文件", None
        
        analysis = analyze_resume_with_llm(content)
        analysis_result = format_llm_analysis_result(analysis)
        
        return analysis_result, analysis
    
    except UnicodeDecodeError:
        return "错误: 文件编码不是UTF-8，请确保文件使用UTF-8编码", None
    except Exception as e:
        return f"错误: {str(e)}", None

def clear_content():
    return "", None

def pdf_to_markdown(pdf_path: str) -> str:
    try:
        markdown_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                
                if text:
                    lines = text.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line:
                            markdown_content.append(line)
                    
                    if page_num < len(pdf.pages):
                        markdown_content.append('')
        
        return '\n'.join(markdown_content)
    
    except Exception as e:
        raise Exception(f"PDF转换失败: {str(e)}")

def analyze_resume_with_llm(content: str) -> Dict[str, any]:
    prompt = f"""请分析以下简历内容，提取关键信息并以JSON格式返回。简历内容如下：

{content}

请提取以下信息并以JSON格式返回：
{{
    "name": "姓名",
    "contact": {{
        "phone": "手机号",
        "email": "邮箱",
        "location": "所在地"
    }},
    "target_position": "求职意向/应聘岗位",
    "skills": ["技能1", "技能2", "技能3"],
    "experience_years": "工作年限",
    "education": "学历信息",
    "summary": "个人简介/自我评价",
    "key_highlights": ["亮点1", "亮点2", "亮点3"]
}}

注意事项：
1. 如果某个信息在简历中找不到，对应字段返回空字符串或空数组
2. skills字段提取所有技术技能、编程语言、框架等
3. key_highlights提取候选人的核心优势或亮点
4. 只返回JSON，不要有其他文字说明
"""

    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=prompt,
            result_format='message'
        )
        
        if response.status_code == 200:
            result_text = response.output.choices[0]['message']['content']
            
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                if not isinstance(result, dict):
                    raise ValueError("返回的不是字典格式")
                
                required_keys = ['name', 'contact', 'target_position', 'skills', 'experience_years', 'education', 'summary', 'key_highlights']
                for key in required_keys:
                    if key not in result:
                        result[key] = "" if key != 'skills' and key != 'key_highlights' else []
                
                if not isinstance(result['contact'], dict):
                    result['contact'] = {'phone': '', 'email': '', 'location': ''}
                
                contact_keys = ['phone', 'email', 'location']
                for key in contact_keys:
                    if key not in result['contact']:
                        result['contact'][key] = ''
                
                return result
            else:
                raise ValueError("无法从响应中提取JSON")
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    except Exception as e:
        print(f"大模型分析出错: {str(e)}")
        return analyze_resume(content)

def format_llm_analysis_result(analysis: Dict[str, any]) -> str:
    output = []
    
    output.append("## 📋 简历分析结果（AI增强版）\n")
    
    if analysis["name"]:
        output.append(f"**姓名**: {analysis['name']}\n")
    
    output.append("### 📞 联系方式")
    if analysis["contact"]["phone"]:
        output.append(f"- 电话: {analysis['contact']['phone']}")
    if analysis["contact"]["email"]:
        output.append(f"- 邮箱: {analysis['contact']['email']}")
    if analysis["contact"]["location"]:
        output.append(f"- 地址: {analysis['contact']['location']}")
    
    if analysis["target_position"]:
        output.append(f"\n### 🎯 求职意向")
        output.append(f"- 应聘岗位: {analysis['target_position']}")
    
    if analysis["experience_years"]:
        output.append(f"- 工作年限: {analysis['experience_years']}")
    
    if analysis["education"]:
        output.append(f"\n### 🎓 学历信息")
        output.append(f"- {analysis['education']}")
    
    if analysis["skills"]:
        output.append(f"\n### 💡 专业技能")
        for skill in analysis["skills"]:
            output.append(f"- {skill}")
    
    if analysis["key_highlights"]:
        output.append(f"\n### ⭐ 核心亮点")
        for highlight in analysis["key_highlights"]:
            output.append(f"- {highlight}")
    
    if analysis["summary"]:
        output.append(f"\n### 👤 个人简介")
        output.append(analysis['summary'])
    
    return '\n'.join(output)

def load_interview_questions(questions_file: str = 'interview_questions.json') -> Dict:
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"categories": {}, "difficulty_levels": {}}

def match_category_from_position(target_position: str, questions_db: Dict) -> List[str]:
    position_lower = target_position.lower()
    matched_categories = []
    
    category_keywords = {
        'frontend': ['前端', 'front-end', 'web前端', 'ui', 'vue', 'react', 'angular', 'javascript', 'typescript'],
        'backend': ['后端', 'back-end', '服务端', 'server', 'api', 'java', 'python', 'go', 'node.js', 'spring'],
        'python': ['python', 'py', '爬虫', '数据分析'],
        'ai_ml': ['ai', '人工智能', '机器学习', 'ml', '深度学习', 'deep learning', 'nlp', '算法'],
        'database': ['数据库', 'database', 'db', 'mysql', 'postgresql', 'mongodb', 'redis'],
        'devops': ['devops', '运维', 'docker', 'kubernetes', 'k8s', 'ci/cd', '部署']
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in position_lower for keyword in keywords):
            matched_categories.append(category)
    
    return matched_categories if matched_categories else ['frontend', 'backend']

def match_category_from_skills(skills: List[str], questions_db: Dict) -> List[str]:
    matched_categories = []
    
    skill_category_mapping = {
        'frontend': ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'webpack', 'vite'],
        'backend': ['java', 'spring', 'node.js', 'express', 'django', 'flask', 'go', 'rust', 'php'],
        'python': ['python', 'pandas', 'numpy', 'scikit-learn', 'django', 'flask'],
        'ai_ml': ['tensorflow', 'pytorch', 'keras', '机器学习', '深度学习', 'nlp', '算法', '模型'],
        'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sql', 'nosql'],
        'devops': ['docker', 'kubernetes', 'k8s', 'git', 'ci/cd', 'linux', 'aws', 'azure', 'gcp']
    }
    
    for category, category_skills in skill_category_mapping.items():
        for skill in skills:
            skill_lower = skill.lower()
            if any(cs in skill_lower for cs in category_skills):
                if category not in matched_categories:
                    matched_categories.append(category)
    
    return matched_categories

def select_questions_by_difficulty(questions: List[Dict], difficulty: str = 'mixed', count: int = 5) -> List[Dict]:
    if difficulty == 'mixed':
        easy_questions = [q for q in questions if q['difficulty'] == 'easy']
        medium_questions = [q for q in questions if q['difficulty'] == 'medium']
        hard_questions = [q for q in questions if q['difficulty'] == 'hard']
        
        import random
        selected = []
        selected.extend(random.sample(easy_questions, min(2, len(easy_questions))))
        selected.extend(random.sample(medium_questions, min(2, len(medium_questions))))
        selected.extend(random.sample(hard_questions, min(1, len(hard_questions))))
        
        if len(selected) < count:
            remaining = count - len(selected)
            all_questions = [q for q in questions if q not in selected]
            selected.extend(random.sample(all_questions, min(remaining, len(all_questions))))
        
        return selected[:count]
    else:
        filtered = [q for q in questions if q['difficulty'] == difficulty]
        import random
        return random.sample(filtered, min(count, len(filtered)))

def generate_interview_questions(analysis: Dict[str, any], questions_file: str = 'interview_questions.json', 
                                 difficulty: str = 'mixed', question_count: int = 5) -> str:
    questions_db = load_interview_questions(questions_file)
    
    if not questions_db['categories']:
        return "## ❌ 面试题库未找到\n\n请确保 interview_questions.json 文件存在。"
    
    target_position = analysis.get('target_position', '')
    skills = analysis.get('skills', [])
    
    matched_categories = []
    
    if target_position:
        position_categories = match_category_from_position(target_position, questions_db)
        matched_categories.extend(position_categories)
    
    if skills:
        skill_categories = match_category_from_skills(skills, questions_db)
        matched_categories.extend(skill_categories)
    
    matched_categories = list(set(matched_categories))
    
    if not matched_categories:
        matched_categories = ['frontend', 'backend']
    
    all_questions = []
    for category in matched_categories:
        if category in questions_db['categories']:
            all_questions.extend(questions_db['categories'][category]['questions'])
    
    if not all_questions:
        return "## ❌ 未找到匹配的面试题\n\n请检查题库配置或简历信息。"
    
    selected_questions = select_questions_by_difficulty(all_questions, difficulty, question_count)
    
    output = []
    output.append("## 📝 推荐面试题\n")
    
    difficulty_names = {
        'easy': '初级',
        'medium': '中级',
        'hard': '高级'
    }
    
    for i, question in enumerate(selected_questions, 1):
        output.append(f"### 题目 {i}")
        output.append(f"**难度**: {difficulty_names.get(question['difficulty'], question['difficulty'])}")
        output.append(f"**问题**: {question['question']}")
        output.append(f"**参考答案**: {question['answer']}")
        output.append(f"**标签**: {', '.join(question['tags'])}")
        output.append("")
    
    output.append(f"\n**匹配的技能类别**: {', '.join(matched_categories)}")
    
    return '\n'.join(output)

with gr.Blocks(title="简历分析器") as demo:
    gr.Markdown("# 📄 简历分析器")
    gr.Markdown("上传简历文件（PDF或Markdown），使用AI大模型自动提取关键信息并生成面试题")
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(
                label="上传简历文件",
                file_types=[".pdf", ".md", ".markdown"],
                type="filepath"
            )
            with gr.Row():
                extract_btn = gr.Button("分析简历", variant="primary")
                clear_btn = gr.Button("清空", variant="secondary")
    
    with gr.Row():
        with gr.Column():
            analysis_output = gr.Markdown(
                label="分析结果",
                value="*分析结果将显示在这里...*"
            )
    
    gr.Markdown("---")
    gr.Markdown("## 🎯 面试题目生成")
    
    with gr.Row():
        difficulty = gr.Radio(
            choices=["mixed", "easy", "medium", "hard"],
            value="mixed",
            label="题目难度",
            info="选择面试题目的难度级别"
        )
        question_count = gr.Slider(
            minimum=1,
            maximum=10,
            value=5,
            step=1,
            label="题目数量",
            info="选择要生成的面试题数量"
        )
        generate_questions_btn = gr.Button("生成面试题", variant="primary")
    
    interview_questions_output = gr.Markdown(
        label="面试题目",
        value="*分析简历后，点击生成面试题按钮...*"
    )
    
    gr.Markdown("""
    ## 使用说明
    
    1. 点击上传按钮选择简历文件（支持PDF、.md、.markdown格式）
    2. 点击"分析简历"按钮，系统会使用AI大模型智能分析简历
       - PDF文件会自动转换为文本格式
       - Markdown文件直接读取内容
    3. 查看分析结果
    4. 选择题目难度和数量
    5. 点击"生成面试题"按钮，系统会根据简历中的技能和岗位自动匹配合适的面试题
    
    ## 分析功能
    
    - **基本信息**: 姓名、联系方式
    - **求职意向**: 应聘岗位、工作年限
    - **专业技能**: AI智能识别技术栈和技能
    - **学历信息**: 教育背景
    - **核心亮点**: AI分析候选人的核心优势
    - **个人简介**: 自我评价和简介
    
    ## 面试题生成
    
    - 根据应聘岗位自动匹配技术类别
    - 根据技能列表智能选择相关题目
    - 支持按难度筛选题目（初级/中级/高级/混合）
    - 提供参考答案和标签
    
    ## 注意事项
    
    - 支持的文件格式: .pdf, .md, .markdown
    - 文件编码必须是UTF-8（Markdown文件）
    - 需要配置通义千问API密钥（已在.env中配置）
    - PDF转换需要安装 pdfplumber 库
    - 建议使用标准简历格式以获得更好的分析效果
    - 面试题库位于 interview_questions.json，可以自定义添加题目
    """)
    
    analysis_state = gr.State(None)
    
    extract_btn.click(
        fn=extract_markdown_content,
        inputs=[file_input],
        outputs=[analysis_output, analysis_state]
    )
    
    clear_btn.click(
        fn=clear_content,
        inputs=[],
        outputs=[analysis_output, analysis_state]
    )
    
    generate_questions_btn.click(
        fn=lambda analysis, diff, count: generate_interview_questions(analysis, difficulty=diff, question_count=count) if analysis else "请先分析简历",
        inputs=[analysis_state, difficulty, question_count],
        outputs=[interview_questions_output]
    )

if __name__ == "__main__":
    demo.launch(server_port=7864)
