# data.orm
from __future__ import annotations
from sqlalchemy import (
    Identity, VARCHAR, REAL, Text, ARRAY,
    PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any

class Base(DeclarativeBase):
    pass


class Base2(DeclarativeBase):
    pass


class Variable(Base2):
    """服务端变量表"""
    name: Mapped[str] = mapped_column(VARCHAR(20), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=False)  # {'value': the_value}

    __tablename__ = "const"


class Domain(Base):
    """领域表"""
    domain_name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sub_domain_name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    domain_id: Mapped[int] = mapped_column(nullable=False)
    sub_domain_id: Mapped[int] = mapped_column(nullable=False)

    questions: Mapped[list[Question]] = relationship(
        back_populates="domain",
        cascade="all, delete-orphan"
    )
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
            ondelete="CASCADE", onupdate="CASCADE",
        ),
    )


class CV(Base):
    """简历表"""
    title: Mapped[str] = mapped_column(VARCHAR(30), primary_key=True)
    basic_info: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    project_experience: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)

    __tablename__ = "cv"


class Job(Base):
    """工作表"""
    name: Mapped[str] = mapped_column(VARCHAR(20), primary_key=True)
    job_requirements: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    job_responsibilities: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    question_banks: Mapped[list[dict[str, str]]] = mapped_column(JSONB(), nullable=False)  # [{'domain': domain_name, 'sub_domain': sub_domain_name}]
    interviewer_name: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=False)

    interviewer: Mapped[Interviewer] = relationship(back_populates="jobs")
    __tablename__ = "job"
    __table_args__ = (
        ForeignKeyConstraint(
            columns=["interviewer_name"], refcolumns=["interviewer.name"],
            ondelete="SET NULL", onupdate="CASCADE",
        ),
    )


class LLM(Base):
    """大模型表"""
    model: Mapped[str] = mapped_column(VARCHAR(30), primary_key=True)
    is_local: Mapped[bool] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    cost: Mapped[float] = mapped_column(REAL(), default=0.)
    cost_limit: Mapped[float] = mapped_column(REAL(), default=1E8)

    interviewers: Mapped[list[Interviewer]] = relationship(
        back_populates="llm",
        cascade="all, delete-orphan"
    )
    __tablename__ = "llm"


class Interviewer(Base):
    """AI 面试官"""
    name: Mapped[str] = mapped_column(VARCHAR(20), primary_key=True)
    model: Mapped[str] = mapped_column(nullable=False,)
    system_prompt: Mapped[str] = mapped_column(Text(), nullable=False)

    llm: Mapped[LLM] = relationship(back_populates="interviewers",)
    jobs: Mapped[list[Job]] = relationship(back_populates="interviewer")
    __tablename__ = "interviewer"
    __table_args__ = (
        ForeignKeyConstraint(
            columns=["model_name"], refcolumns=["llm.model"],
            ondelete="SET NULL", onupdate="CASCADE",
        ),
    )


