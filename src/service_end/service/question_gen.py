from ..data.model import QuestionModel


async def question_gen_workflow(
        domain_name: str,
        sub_domain_name: str,
        number: int
) -> list[QuestionModel]:
    """问题生成工作流 (待实现)"""
    # 用于测试
    return [
        QuestionModel(
            question="how much is 1+2",
            answer="it's 3",
            criterion_low="answer irrelevant to question",
            criterion_mid="answer around 2 to 4",
            criterion_high="answer correct"
        )
    ] * number
