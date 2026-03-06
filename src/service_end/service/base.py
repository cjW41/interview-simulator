from ..exception import ServiceException, LLMEmptyResponse
from ..data.model import LLMCard
from langchain_core.messages.ai import AIMessage, AIMessageChunk, add_ai_message_chunks
from langchain_openai import ChatOpenAI
from typing import Sequence


CHARGE_UNIT = 1E6  # 一百万


class ParsedAIMessage:

    def __init__(self, ai_message: AIMessage | Sequence[AIMessageChunk], llm_card: LLMCard) -> None:
        """大模型输出信息提取"""
        (
            self.content,
            self.token_charge_prompt,
            self.token_charge_completion,
            self.prompt_tokens,
            self.completion_tokens
        ) = ParsedAIMessage.__parse_AIMessage_ChatOpenAI(ai_message, llm_card)

    @classmethod
    def __parse_AIMessage_ChatOpenAI(
            cls,
            ai_message: AIMessage | Sequence[AIMessageChunk],
            llm_card: LLMCard
    ) -> tuple[str, float, float, int, int]:
        """
        从 AIMessage 提取信息

        Args:
            ai_message (AIMessage | Sequence[AIMessageChunk]): ChatOpenAI 返回的响应对象
            llm_card (LLMCard): 大模型配置
        
        Returns:
            content (str): AI 响应
            token_charge_prompt (float): AI 输入计费
            token_charge_completion (float): AI 输出计费
            prompt_tokens (int): prompt Token 数
            completion_tokens (int): completion Token 数

        Note:
            ```
            # ChatOpenAI 返回的 AIMessage:
            AIMessage(
                content="J'adore la programmation.",
                response_metadata={
                    "token_usage": {
                        "completion_tokens": 5,
                        "prompt_tokens": 31,
                        "total_tokens": 36,
                    },
                    "model_name": "gpt-4o",
                    "system_fingerprint": "fp_43dfabdef1",
                    "finish_reason": "stop",
                    "logprobs": None,
                },
                id="run-012cffe2-5d3d-424d-83b5-51c6d4a593d1-0",
                usage_metadata={"input_tokens": 31, "output_tokens": 5, "total_tokens": 36},
            )

            # ChatOpenAI 流式输出 (最后一个 chunk 含有 response_metadata)
            [
                AIMessageChunk(content=" programmation", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
                AIMessageChunk(content=".", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
                AIMessageChunk(
                    content="",
                    response_metadata={"finish_reason": "stop"},
                    id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0",
                )
            ]
            ```
        """
        if isinstance(ai_message, AIMessage):
            ai_message_ = ai_message
        else:    
            if len(ai_message) == 1:
                raise LLMEmptyResponse()
            ai_message_ = add_ai_message_chunks(ai_message[0], *ai_message[1:])  # 合并所有回复

        content = ai_message_.content
        assert isinstance(content, str)

        token_usages: dict = ai_message_.response_metadata["token_usages"]
        prompt_tokens = token_usages["prompt_tokens"]
        competion_tokens = token_usages["completion_tokens"]

        
        if llm_card.is_local:
            return (content, -1., -1., prompt_tokens, competion_tokens)
        else:
            if (llm_card.token_charge_prompt_unit > 0) and (llm_card.token_charge_completion_unit > 0)
                return (
                    content,
                    llm_card.token_charge_prompt_unit * (prompt_tokens / CHARGE_UNIT),
                    llm_card.token_charge_completion_unit * (competion_tokens / CHARGE_UNIT),
                    prompt_tokens, competion_tokens
                )
            else:  # LLMCard 计费存在问题
                raise ServiceException(f"prompt/completion charge unit of non-local model {llm_card.model} is non-positive")


class LLMChargeTracker:

    def __init__(self,
                 llm_card: LLMCard,
                 *,
                 initial_charge: float = 0.,
                 warning_threshold_percentage: float = 0.9):
        """
        大模型调用费用追踪。
        
        Args:
            llm_card: 大模型配置
        """
        self.model = llm_card.model
        self.charge = initial_charge
    
    def add_










