import os
import json
from typing import Optional, Dict, Any


class LLMClient:
    """大模型客户端"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """初始化大模型客户端
        
        Args:
            model_name: 模型名称
            api_key: API密钥
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            
        Returns:
            str: 生成的文本
        """
        # 这里使用模拟实现，实际项目中应该调用真实的大模型API
        # 例如OpenAI API、Anthropic API等
        print(f"使用大模型生成文本...")
        print(f"系统提示词: {system_prompt}")
        print(f"用户提示词: {prompt}")
        
        # 模拟大模型响应
        # 在实际项目中，这里应该调用真实的大模型API
        return '''{
            "name": "张三",
            "gender": "男",
            "age": 28,
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "address": "北京市朝阳区",
            "education": [
                {
                    "school": "北京大学",
                    "major": "计算机科学与技术",
                    "degree": "硕士",
                    "start_date": "2018-09",
                    "end_date": "2021-06",
                    "gpa": 3.8
                },
                {
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "degree": "学士",
                    "start_date": "2014-09",
                    "end_date": "2018-06",
                    "gpa": 3.9
                }
            ],
            "work_experience": [
                {
                    "company": "ABC科技有限公司",
                    "position": "高级软件工程师",
                    "start_date": "2021-07",
                    "end_date": "2023-12",
                    "description": "负责后端系统的设计和开发，参与架构设计和技术选型，带领团队完成多个重要项目。设计并实现了分布式缓存系统，提升系统性能30%。主导了微服务架构改造，提高了系统的可扩展性。"
                },
                {
                    "company": "XYZ互联网公司",
                    "position": "软件工程师",
                    "start_date": "2019-07",
                    "end_date": "2021-06",
                    "description": "参与后端开发，负责API开发和数据库设计。"
                }
            ],
            "project_experience": [
                {
                    "name": "智能推荐系统",
                    "role": "核心开发者",
                    "start_date": "2022-01",
                    "end_date": "2022-06",
                    "description": "基于用户行为数据，开发智能推荐系统，提高用户活跃度20%。",
                    "technologies": ["Python", "TensorFlow", "Redis", "Kafka"]
                },
                {
                    "name": "电商平台后端系统",
                    "role": "开发者",
                    "start_date": "2020-03",
                    "end_date": "2020-09",
                    "description": "开发电商平台的后端系统，支持商品管理、订单处理等功能。",
                    "technologies": ["Java", "Spring Boot", "MySQL", "Redis"]
                }
            ],
            "skills": [
                {"category": "技术技能", "items": ["Python", "Java", "C++", "JavaScript", "React", "Vue", "Spring Boot", "Django", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS"]},
                {"category": "语言技能", "items": ["英语（流利）", "日语（基础）"]},
                {"category": "软技能", "items": ["团队协作", "沟通能力", "问题解决能力", "领导力"]}
            ],
            "certificates": ["阿里云架构师认证", "AWS Certified Solutions Architect", "PMP项目管理认证"],
            "self_evaluation": "我是一个充满激情的软件工程师，具有扎实的技术基础和丰富的项目经验。我善于学习新技术，能够快速适应新环境，并且具有良好的团队协作能力。我希望能够在一个充满挑战的环境中继续成长，为公司的发展贡献自己的力量。",
            "interests": ["编程", "阅读", "跑步", "旅游"]
        }'''  
    
    def extract_resume_info(self, resume_text: str) -> Dict[str, Any]:
        """提取简历信息
        
        Args:
            resume_text: 简历文本
            
        Returns:
            Dict[str, Any]: 提取的简历信息
        """
        system_prompt = "你是一个专业的简历信息提取助手，能够从简历文本中提取结构化信息。请按照指定的JSON格式返回提取结果。"
        
        prompt = f"请从以下简历文本中提取结构化信息，包括：个人基本信息（姓名、性别、年龄、电话、邮箱、地址）、教育背景、工作经历、项目经验、技能、证书、自我评价和兴趣爱好。\n\n{resume_text}\n\n请以JSON格式返回提取结果，确保格式正确。"
        
        response = self.generate(prompt, system_prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
