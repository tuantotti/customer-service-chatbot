from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)


class PredefinedPrompt:
    def __init__(self) -> None:
        _condense_question_template = """Với cuộc trò chuyện sau đây và một câu hỏi tiếp theo, hãy diễn đạt lại câu hỏi tiếp theo thành một câu hỏi độc lập, bằng ngôn ngữ gốc của nó.

        Lịch sử trò chuyện::
        {chat_history}
        Đầu vào tiếp theo: {question}
        Câu hỏi độc lập:"""
        self.CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
            _condense_question_template
        )

        _answer_template = """Trả lời câu hỏi chỉ dựa trên ngữ cảnh sau:
        {context}

        Câu hỏi: {question}
        """
        self.ANSWER_PROMPT = ChatPromptTemplate.from_template(_answer_template)

        review_template_str = """Công việc của bạn là tư vấn sản phẩm. Sử dụng bối cảnh sau đây để trả lời các câu hỏi. Càng chi tiết càng tốt, nhưng đừng bịa đặt bất kỳ thông tin nào đó không phải từ bối cảnh. Nếu bạn không biết câu trả lời, hãy nói bạn không biết.

        {context}
        """

        review_system_prompt = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["context"],
                template=review_template_str,
            )
        )

        review_human_prompt = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["question"],
                template="{question}",
            )
        )
        messages = [review_system_prompt, review_human_prompt]

        self.review_prompt_template = ChatPromptTemplate(
            input_variables=["context", "question"],
            messages=messages,
        )
