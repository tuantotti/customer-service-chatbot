from typing import AnyStr

from langchain.prompts import ChatPromptTemplate, PromptTemplate

from chatbot.utils import SingletonMeta
from configs.config import llm_config


class PredefinedPrompt(metaclass=SingletonMeta):
    def __init__(self) -> None:
        """Initial params of prompt"""
        inference_params = llm_config["inference_params"]
        self.input_prefix = inference_params["input_prefix"]
        self.input_suffix = inference_params["input_suffix"]
        self.input = inference_params["input"]
        self.pre_prompt = inference_params["pre_prompt"]
        self.pre_prompt_prefix = inference_params["pre_prompt_prefix"]
        self.pre_prompt_suffix = inference_params["pre_prompt_suffix"]
        self.condense_question_prompt = inference_params["condense_question_prompt"]

        self.ANSWER_PROMPT = self.get_answer_prompt()
        self.CONDENSE_QUESTION_PROMPT = self.get_condense_prompt()

    def get_answer_prompt(self) -> ChatPromptTemplate:
        """Create prompt for answering questions

        Returns:
            ChatPromptTemplate: the prompt template for answering questions
        """
        template = f"{self.pre_prompt_prefix}\n{self.pre_prompt}\n{self.pre_prompt_suffix}\n\n{self.input} {self.input_suffix}"
        prompt_template = ChatPromptTemplate.from_template(template=template)

        return prompt_template

    def get_system_prompt(self) -> AnyStr:
        """Create system prompt

        Returns:
            AnyStr: the system prompt
        """
        return (
            f"{self.pre_prompt_prefix}\n{self.pre_prompt}\n{self.pre_prompt_suffix}\n\n"
        )

    def get_human_prompt(self) -> AnyStr:
        """Create human prompt

        Returns:
            AnyStr: the human prompt
        """
        return f"{self.input_prefix}" + "{question}" + f"{self.input_suffix}"

    def get_condense_prompt(self) -> PromptTemplate:
        """Create prompt for question generation

        Returns:
            PromptTemplate: prompt template for question generation
        """
        template = (
            self.pre_prompt_prefix
            + self.condense_question_prompt
            + self.pre_prompt_suffix
        )
        condense_question_prompt = PromptTemplate.from_template(template)

        return condense_question_prompt
