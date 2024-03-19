from langchain_core.output_parsers import StrOutputParser

from chatbot.embedd import EmbeddingModel
from chatbot.generator import Generator
from chatbot.prompts import PredefinedPrompt
from chatbot.retriever import Retriever
from configs.config import llm_config


class CustomerServiceChatbot:
    def __init__(self, use_retriever=False, is_hf_model=False) -> None:
        self.is_hf_model = is_hf_model
        self.use_retriever = use_retriever
        self.chain = self.init_chain()

    def init_chain(self):
        chat_template = PredefinedPrompt()
        embedding_model = EmbeddingModel()
        retriever = Retriever(embedding_model=embedding_model)
        generator = Generator(model_params=llm_config["model_params"])
        if self.use_retriever:
            chain = chat_template.review_prompt_template | retriever
        else:
            chain = chat_template.review_prompt_template | generator | StrOutputParser()

        return chain

    def invoke(self, query={"context": "", "question": ""}):
        return self.chain.invoke(query)
