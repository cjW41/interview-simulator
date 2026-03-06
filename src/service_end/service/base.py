from ..exception import LLMResponseError, ContextWindowError
from ..data.model import LLMCard, MessageModel
import os
from enum import Enum
from typing import Callable, Sequence
from collections.abc import AsyncIterator
from langchain_core.messages import BaseMessage, BaseMessageChunk, AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langchain_core.messages.ai import  add_ai_message_chunks
from langchain_openai import ChatOpenAI
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnableConfig


class ResponseStatus(Enum):
    """
    响应生成的状态。
        completed: 生成完成
        failed: 生成失败
        in_progressv生成中
        cancelled: 已取消
        queued: 请求排队中
        incomplete: 生成不完整
    """
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESSV = "in_progressv"
    CANCELLED = "cancelled"
    QUEUED = "queued"
    INCOMPLETE = "incomplete"


class ContextWindow:

    def __init__(self, max_tokens: int, token_counter: Callable[[Sequence[BaseMessage]], int] | None,) -> None:
        """
        Agent 上下文窗口
        
        Args:
            max_tokens (int): 最大上下文
            token_counter (Callable[[Sequence[BaseMessage]], int] | None): 上下文计数器
        """
        if max_tokens <= 0:  # 不剪裁
            trimmer = ContextWindow.__identity_trimmer
        else:
            if token_counter is None:  # 使用近似 token 估计剪裁
                from langchain_core.messages.utils import count_tokens_approximately
                token_counter = count_tokens_approximately
            trimmer = trim_messages(
                max_tokens=max_tokens,
                token_counter=token_counter,
                include_system=True,
                allow_partial=False,
                start_on="human",
            )
        self.token_trimmer = trimmer  # 通过 invoke 方法剪裁 list[BaseMessage]
        self.__full_context: list[BaseMessage] = []  # 完整上下文

    @classmethod
    def __identity_trimmer(cls, messages: Sequence[BaseMessage], **kwargs) -> Sequence[BaseMessage]:
        return messages

    @property
    def context(self, **kwargs) -> Sequence[BaseMessage]:
        """当前经过剪裁的上下文"""
        return self.token_trimmer(self.__full_context, **kwargs)

    def add_message(self, message: BaseMessage):
        """将新消息添加到上下文末尾"""
        self.__full_context.append(message)

    def add_streaming_ai_message(self, chunks: list[AIMessageChunk]):
        """将新的流式输出的一组 AI 消息块拼接为 AI消息"""
        if len(chunks) <= 1:
            raise LLMResponseError("empty streaming response")
        merged_chunk = add_ai_message_chunks(chunks[0], *chunks[1:])
        self.__full_context.append(
            AIMessage(
                content=merged_chunk.content,
                response_metadata=merged_chunk.response_metadata,
                additional_kwargs=merged_chunk.additional_kwargs,
                tool_calls=merged_chunk.tool_call_chunks,
                invalid_tool_calls=merged_chunk.invalid_tool_calls,
                usage_metadata=merged_chunk.usage_metadata,
            )
        )

    def dump_as_MessageModel(self) -> list[MessageModel]:
        """将上下文中有价值部分保存为字典的列表"""
        context: list[MessageModel] = []
        for msg in self.__full_context:  # 遍历 Human/AI/ToolMessage
            content = msg.content
            assert isinstance(content, str)
            data: dict = {"message_type": msg.__class__.__name__, "content": content}

            if isinstance(msg, HumanMessage):
                pass
            elif isinstance(msg, AIMessage):
                data.update(  # tool_calls & invalid_... 都是 TypedDict
                    {
                        "tool_calls": msg.tool_calls,
                        "invalid_tool_calls": msg.invalid_tool_calls
                    }
                )
            elif isinstance(msg, ToolMessage):
                data.update(
                    {"status": msg.status}
                )
            else:
                msg_class = msg.__class__.__name__
                if isinstance(msg, BaseMessage):
                    raise ContextWindowError(f"subclass of BaseMessage {msg_class} is not supported")
                else:
                    raise ContextWindowError(f"an unsupported {msg_class} object is added to context window")
            
            context.append(MessageModel(**data))
        return context


class AgentBase:

    def __init__(self,
                 llm_card: LLMCard,
                 trim_threshold: float,
                 token_counter: Callable[[Sequence[BaseMessage]], int] | None,
                 streaming: bool,
                 enable_thinking: bool,
                 temperature: float | None,
                 top_p: float | None,
                 top_k: int | None,
                 **kwargs):
        """
        使用 langchain ChatOpenAI 构建的大模型 Agent

        Args:
            llm_card (LLMCard): 大模型
            trim_threshold (float): 上下文参数。剪裁阈值，设为**非正数**时不进行剪裁，设为超过 1 的值抛出异常
            token_counter (Callable | None): 上下文参数。Token 计数函数
            streaming (bool): 推理参数。是否启用流式输出
            enable_thinking (bool): 推理参数。是否启用思考
            temperature (float): 推理参数。推理温度
            top_p (float): 推理参数。top-p 采样值
            top_k (int): 推理参数。top-k 采样值
            kwargs: 其余传递给 ChatOpenAI 的参数
        """
        api_key = os.getenv(llm_card.api_key_name)
        assert api_key is not None
        assert llm_card.context_window_size > 0
        args: dict = {"name": llm_card.model, "base_url": llm_card.path, "api_key": api_key,}
        if streaming:
            args["stream"] = True
        if enable_thinking:
            args["extra_body"] = {"enable_thinking": True}
        if temperature is not None:
            args["temperature"] = temperature
        if top_k is not None:
            args["top_k"] = top_k
        if top_p is not None:
            args["top_p"] = top_p
        args.update(kwargs)
        self.llm = ChatOpenAI(**args) # type:ignore

        self.context_window = ContextWindow(
            max_tokens=int(trim_threshold * llm_card.context_window_size),
            token_counter=token_counter
        )
        self.llm_card = llm_card

    async def ainvoke(
            self,
            new_message: HumanMessage | ToolMessage,
            config: RunnableConfig | None = None
        ) -> BaseMessage:
        """调用 ChatOpenAI.ainvoke，自动传入上下文"""
        self.context_window.add_message(message=new_message)
        response_message = await self.llm.ainvoke(self.context_window.context, config=config)
        return response_message

    async def astream(
            self,
            new_message: HumanMessage | ToolMessage,
            config: RunnableConfig | None = None
    ) -> AsyncIterator[BaseMessageChunk]:
        """
        调用 ChatOpenAI.astream，自动传入上下文
        ```
        async for chunk in (await self.astream(message)):
            ...
        ```
        """
        self.context_window.add_message(message=new_message)
        return self.llm.astream(self.context_window.context, config=config)

