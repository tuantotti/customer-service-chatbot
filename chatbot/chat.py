from operator import itemgetter

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from chatbot.embedd import EmbeddingModel
from chatbot.generator import Generator
from chatbot.prompts import PredefinedPrompt
from chatbot.retriever import VectorStore
from configs.config import llm_config
from rest_api.schemas.items import QueryItem


class CustomerServiceChatbot:
    def __init__(self, use_retriever=False, is_hf_model=False) -> None:
        self.is_hf_model = is_hf_model
        self.use_retriever = use_retriever
        self.memory = self.init_memory()
        self.chain = self.init_chain()

    def get_history(self):
        self.history = RunnablePassthrough.assign(
            chat_history=RunnableLambda(self.memory.load_memory_variables)
            | itemgetter("history")
        )

    def init_chain(self):
        prompt = PredefinedPrompt()
        self.ANSWER_PROMPT = prompt.ANSWER_PROMPT
        self.CONDENSE_QUESTION_PROMPT = prompt.CONDENSE_QUESTION_PROMPT

        generator = Generator(model_params=llm_config["model_params"])
        self.llm = generator.model

        self.output_parser = StrOutputParser()

        if self.use_retriever:
            chain = self.get_conversional_chain()
        else:
            chain = self.get_answer_chain()

        return chain

    def invoke(self, query: QueryItem):
        answer = None
        if query.context:
            answer = self.chain.invoke(query.dict())
        return answer

    def init_memory(self):
        memory = ConversationBufferMemory(
            return_messages=True, output_key="answer", input_key="question"
        )

        return memory

    def get_answer_chain(self):
        self.answer_chain = (
            self.CONDENSE_QUESTION_PROMPT | self.llm | self.output_parser
        )

        return self.answer_chain
    
    def get_conversional_chain(self):
        loaded_memory = RunnablePassthrough.assign(
            chat_history=RunnableLambda(self.memory.load_memory_variables)
            | itemgetter("history"),
        )

        embedding_model = EmbeddingModel()
        vector_store = VectorStore(embedding_model=embedding_model.model)
        self.retriever = vector_store.get_retriever()

        standalone_question = {
                "standalone_question": {
                    "question": lambda x: x["question"],
                    "chat_history": lambda x: get_buffer_string(x["chat_history"]),
                }
                | self.CONDENSE_QUESTION_PROMPT
                | self.llm,
            }

        retrieved_documents = {
            "docs": itemgetter("standalone_question") | self.retriever,
            "question": lambda x: x["standalone_question"],
        }

        final_inputs = {
            "context": lambda x: x["docs"],
            "question": itemgetter("question"),
        }

        answer = {
            "answer": final_inputs | self.ANSWER_PROMPT | self.llm,
            "question": itemgetter("question"),
            "context": final_inputs["context"],
        }

        chain = loaded_memory | standalone_question | retrieved_documents | answer

        return chain


