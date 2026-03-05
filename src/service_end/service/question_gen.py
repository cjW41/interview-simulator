import os
import json
import asyncio
from ..data.model import QuestionModel
from ..exception import QuestionGenException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 初始化模型
model = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), # type: ignore
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.7
)

# 定义提示模板
prompt_template = ChatPromptTemplate.from_template("""
你是一位专业的技术面试官，擅长为各种岗位创建结构化的面试题库。

请为以下领域创建面试题库：
领域名称：{domain_name}
子领域名称：{sub_domain_name}

要求：
1. 为该子领域生成{number}道面试题
2. 每道题包含：
   - 题目描述
   - 参考答案（要求简洁明了，控制在100字以内）
   - 评分标准（优秀、良好、差三个等级，每个等级控制在50字以内）
3. 题目难度应覆盖基础、中级和高级
4. 题目应与该领域紧密相关
5. 评分标准应具体、可操作

输出格式：JSON格式，结构如下：
{{
  "domain_name": "领域名称",
  "sub_domain_name": "子领域名称",
  "questions": [
    {{
      "id": "领域_子领域_001",
      "question": "题目描述",
      "answer": "参考答案",
      "evaluation": {{
        "excellent": "优秀标准",
        "good": "良好标准",
        "poor": "差标准"
      }}
    }}
  ]
}}

请直接输出JSON格式，不要包含其他内容。
""")

# 创建输出解析器
output_parser = StrOutputParser()

# 构建工作流
chain = prompt_template | model | output_parser

async def question_gen_workflow(
        domain_name: str,
        sub_domain_name: str,
        number: int
) -> list[QuestionModel]:
    """问题生成工作流"""
    print(f"正在为领域 '{domain_name}' 的子领域 '{sub_domain_name}' 生成 {number} 道题目...")
    
    try:
        # 计算需要的批次数
        batch_size = 5  # 每批生成5道题
        total_batches = (number + batch_size - 1) // batch_size
        
        # 定义异步处理单个批次的函数
        async def process_batch(batch_num):
            print(f"正在生成第 {batch_num}/{total_batches} 批题目...")
            try:
                # 使用异步调用
                result = await chain.ainvoke({
                    "domain_name": domain_name,
                    "sub_domain_name": sub_domain_name,
                    "number": batch_size
                })
                
                # 预处理
                if result.startswith('```json'):
                    result = result[7:]
                if result.endswith('```'):
                    result = result[:-3]
                result = result.strip()
                
                # 解析JSON
                domain_data = json.loads(result)
                
                # 转换为QuestionModel
                questions = []
                for i, q_data in enumerate(domain_data.get("questions", [])):
                    question = QuestionModel(
                        question=q_data.get("question"),
                        answer=q_data.get("answer"),
                        criterion_low=q_data.get("evaluation", {}).get("poor", "回答错误或与问题无关"),
                        criterion_mid=q_data.get("evalguation", {}).get("good", "回答基本正确，但不够全面"),
                        criterion_high=q_data.get("evaluation", {}).get("excellent", "回答完全正确，且深入全面")
                    )
                    questions.append(question)
                
                print(f"成功生成第 {batch_num} 批题目，包含 {len(questions)} 道题目")
                return questions
            except Exception as e:
                print(f"生成第 {batch_num} 批题目失败: {e}")
                return []
        
        # 生成所有批次的任务
        batch_tasks = []
        for batch_num in range(1, total_batches + 1):
            batch_tasks.append(process_batch(batch_num))
        
        # 并行执行所有批次
        batches_results = await asyncio.gather(*batch_tasks)
        
        # 合并所有批次的题目
        all_questions = []
        for batch_questions in batches_results:
            all_questions.extend(batch_questions)
        
        # 限制题目数量
        all_questions = all_questions[:number]
        
        print(f"成功生成 {len(all_questions)} 道题目")
        return all_questions
    except Exception as e:
        raise QuestionGenException() from e  

        
