from abc import ABC, abstractmethod
from typing import AnyStr, List

from langchain.prompts import ChatPromptTemplate, PromptTemplate

from configs.config import llm_config


class BasePrompt(ABC):
    @staticmethod
    def apply_chat_template(conversations: List) -> AnyStr:
        raise NotImplementedError("apply_chat_template is not implemented")


class MistralPrompt(BasePrompt):
    @staticmethod
    def apply_chat_template(conversations: List) -> AnyStr:
        bos_token = "<s>"
        eos_token = "</s>"
        if conversations[0]["role"] == "system":
            loop_messages = conversations[1:]
            system_message = conversations[0]["content"]
        else:
            loop_messages = conversations
            system_message = False

        result = []

        for index, message in enumerate(loop_messages):
            if (message["role"] == "user") != (index % 2 == 0):
                raise Exception(
                    "Conversation roles must alternate user/assistant/user/assistant/..."
                )

            if index == 0 and system_message:
                content = (
                    f'<<SYS>> \n{system_message}\n<</SYS>> \n\n{message["content"]}'
                )
            else:
                content = message["content"]

            if message["role"] == "user":
                formatted_message = f"{bos_token}[INST]  {content.strip()} [/INST]"
            elif message["role"] == "assistant":
                formatted_message = f"  {content.strip()} {eos_token}"

            result.append(formatted_message)

        return "".join(result)


class PredefinedPrompt:
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
