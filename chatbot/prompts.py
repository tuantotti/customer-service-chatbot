from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               PromptTemplate, SystemMessagePromptTemplate)

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

        self.prompt_template = self.format_prompt()

    def format_prompt(self):
        template = f"""{self.pre_prompt_prefix}\n{self.pre_prompt}\n{self.pre_prompt_suffix}\n\n{self.input} {self.input_suffix}"""
        prompt_template = ChatPromptTemplate.from_template(template=template)
        
        return prompt_template