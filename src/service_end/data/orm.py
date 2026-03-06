# data.orm
from __future__ import annotations
from .utils.enum_ import AgentRole, InterviewPhase, MessageType
from sqlalchemy import (
    Identity, VARCHAR, Text, ARRAY, TIMESTAMP, BOOLEAN, Integer,
    PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB
import datetime
from typing import Any


class Base(DeclarativeBase):
    pass


class Domain(Base):
    """领域表"""
    domain_name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    sub_domain_name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    domain_id: Mapped[int] = mapped_column(nullable=False)
    sub_domain_id: Mapped[int] = mapped_column(nullable=False)

    __tablename__ = "domain"
    __table_args__ = (
        PrimaryKeyConstraint("domain_id", "sub_domain_id"),
        UniqueConstraint("domain_name", "sub_domain_name"),
    )


class Question(Base):
    """问题表。外键关联 `domain` 表。级联更新与删除。"""
    id_: Mapped[int] = mapped_column(Identity(start=1), name="id", primary_key=True)
    domain_id: Mapped[int] = mapped_column(nullable=False)
    sub_domain_id: Mapped[int] = mapped_column(nullable=False)
    question: Mapped[str] = mapped_column(Text(), nullable=False)
    answer: Mapped[str] = mapped_column(Text(), nullable=False)
    criterion_low: Mapped[str] = mapped_column(Text(), nullable=False)
    criterion_mid: Mapped[str] = mapped_column(Text(), nullable=False)
    criterion_high: Mapped[str] = mapped_column(Text(), nullable=False)

    __tablename__ = "question"
    __table_args__ = (
        ForeignKeyConstraint(
            columns=["domain_id", "sub_domain_id"],
            refcolumns=["domain.domain_id", "domain.sub_domain_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="domain_question_Fkey",
        ),
    )


class CV(Base):
    """简历表"""
    title: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    basic_info: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    project_experience: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)

    __tablename__ = "cv"


class Job(Base):
    """工作表"""
    name: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    job_requirements: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    job_responsibilities: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)

    __tablename__ = "job"



class LLM(Base):
    """大模型表"""
    model: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    path: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    context_window_size: Mapped[int] = mapped_column(nullable=False)
    api_key_name: Mapped[str] = mapped_column(nullable=False)

    interviewers: Mapped[list[Interviewer]] = relationship(
        back_populates="llm",
        cascade="all, delete-orphan"
    )
    __tablename__ = "llm"


class Interviewer(Base):
    """AI 面试官"""
    name: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    model: Mapped[str] = mapped_column(nullable=False,)
    system_prompt: Mapped[str] = mapped_column(Text(), nullable=False)

    llm: Mapped[LLM] = relationship(back_populates="interviewers")
    __tablename__ = "interviewer"
    __table_args__ = (
        ForeignKeyConstraint(
            columns=["model"],
            refcolumns=["llm.model"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="llm_interviewer_Fkey",
        ),
    )


class Interview(Base):
    """面试表"""
    id_: Mapped[int] = mapped_column(Integer(), name="id", primary_key=True)
    start_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    end_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    cv_title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    interviewer_name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    job_name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    report: Mapped[str] = mapped_column(Text(), nullable=False)

    messages: Mapped[list[Message]] = relationship(back_populates="message")
    __tablename__ = "interview"
    __table_args__ = (
        ForeignKeyConstraint(
            columns=["cv_title"],
            refcolumns=["cv.title"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="cv_interview_Fkey",
        ),
        ForeignKeyConstraint(
            columns=["interviewer_name"],
            refcolumns=["interviewer.name"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="interviewer_interview_Fkey",
        ),
        ForeignKeyConstraint(
            columns=["job_name"],
            refcolumns=["job.name"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="job_interviewer_Fkey",
        ),
    )


class Message(Base):
    """Langchain Message"""
    interview_id: Mapped[int] = mapped_column(nullable=False)
    message_id: Mapped[int] = mapped_column(nullable=False)  # Message (在整场 interview 中) 的序号
    interview_phase: Mapped[InterviewPhase] = mapped_column(nullable=False)
    agent_role: Mapped[AgentRole] = mapped_column(nullable=False)
    
    message_type: Mapped[MessageType] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    tool_calls: Mapped[dict] = mapped_column(JSONB(), nullable=True)
    invalid_tool_calls: Mapped[dict] = mapped_column(JSONB(), nullable=True)
    succeeded: Mapped[bool] = mapped_column(BOOLEAN(), nullable=True)

    interview: Mapped[Interview] = relationship(back_populates="interview")
    __tablename__ = "message"
    __table_args__ = (
        PrimaryKeyConstraint("interview_id", "message_id"),
        ForeignKeyConstraint(
            columns=["interview_id"],
            refcolumns=["interview.id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="interview_message_Fkey",
        )
    )

