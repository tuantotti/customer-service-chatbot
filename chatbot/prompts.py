from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                               PromptTemplate)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from configs.config import llm_config


class PredefinedPrompt:
    def __init__(self) -> None:
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

    def get_answer_prompt(self):
        template = f"{self.pre_prompt_prefix}\n{self.pre_prompt}\n{self.pre_prompt_suffix}\n\n{self.input} {self.input_suffix}"
        prompt_template = ChatPromptTemplate.from_template(template=template)

        return prompt_template

    def get_system_prompt(self):
        return (
            f"{self.pre_prompt_prefix}\n{self.pre_prompt}\n{self.pre_prompt_suffix}\n\n"
        )

    def get_human_prompt(self):
        return f"{self.input_prefix}" + "{question}" + f"{self.input_suffix}"

    def get_condense_prompt(self) -> PromptTemplate:
        template = (
            self.pre_prompt_prefix
            + self.condense_question_prompt
            + self.pre_prompt_suffix
        )
        condense_question_prompt = PromptTemplate.from_template(template)

        return condense_question_prompt
