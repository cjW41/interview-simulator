from enum import Enum

class SequenceName(Enum):
    """数据库中和表关联的 Sequence"""
    DOMAIN = "DOMAIN"
    INTERVIEW = "INTERVIEW"


class AgentRole(Enum):
    """Agent 角色(名称)"""
    INTERVIEWER = "interviewer"
    ASSISTANT = "assistant"
    IMPRESSION_SCORER = "impression_scorer"
    REPORT_WRITER = "report_writer"


class InterviewPhase(Enum):
    """面试阶段"""
    BASIS = "basis"      # 基础知识提问
    PROJECT = "project"  # 项目提问
    FREE = "free"        # 自由提问


class MessageType(Enum):
    """Langchain Message 类型"""
    AIMessage = "AIMessage"
    HumanMessage = "HumanMessage"
    ToolMessage = "ToolMessage"


