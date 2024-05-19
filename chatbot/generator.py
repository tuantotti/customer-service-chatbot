from typing import Any, AnyStr, Dict, List

from chatbot.utils import SingletonMeta


class Generator(metaclass=SingletonMeta):
    def __init__(self, model_params: Dict) -> None:
        """Initial a generator model

        Args:
            model_params (Dict): the params of the generator model
        """
        self.model_params = model_params
        self.model_path = self.model_params["model_path"]
        self.model = self.get_model()

    def get_model(self) -> Any:
        """Create a generator model

        Returns:
            Any: the loaded model
        """
        llm = None
        if self.model_path.endswith(".gguf"):
            from langchain_community.llms import LlamaCpp

            # Use llama-cpp-python library to load model
            llm = LlamaCpp(**self.model_params)

        return llm

    def invoke(self, messages: List) -> List:
        """Invoke the generator model

        Args:
            messages (List): list of incoming questions

        Returns:
            List: list of answer for the incoming questions
        """
        return self.model.invoke(messages)
