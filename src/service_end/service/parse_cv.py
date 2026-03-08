import json
from ..data.model import CVModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


async def parse_cv_workflow(cv_str: str, title: str) -> CVModel:
    llm = ChatOpenAI(
        model="deepseek-chat",
        temperature=0,
    )
    
    schema = CVModel.model_json_schema()
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个简历解析助手。请从用户提供的简历中提取结构化信息。

请严格按照以下 JSON Schema 格式返回结果，不要输出任何其他内容：
{schema}"""),
        ("human", "请解析以下简历内容：\n\n{cv_content}")
    ])
    
    chain = prompt | llm
    
    response = await chain.ainvoke({
        "cv_content": cv_str,
        "schema": schema_str
    })
    
    content = response.content
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    data = json.loads(content)
    result = CVModel.model_validate(data)
    result.title = title
    return result
