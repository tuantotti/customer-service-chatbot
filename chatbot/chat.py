from operator import itemgetter
from typing import Dict, Union

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (RunnableLambda, RunnableParallel,
                                      RunnablePassthrough)

from chatbot.embedd import EmbeddingModel
from chatbot.generator import Generator
from chatbot.prompts import PredefinedPrompt
from chatbot.retriever import VectorStore
from configs.config import llm_config
from rest_api.schemas.items import QueryItem, QuestionItem
from utils.logger import Logger

logger = Logger.get_logger()


class CustomerServiceChatbot:
    def __init__(self, use_retriever=True, use_chat_history=False) -> None:
        """Initial params

        Args:
            use_retriever (bool, optional): this flag checks whether using retriever model. Defaults to False.
        """
        self.use_retriever = use_retriever
        self.use_chat_history = use_chat_history
        embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(embedding_model=embedding_model.model)
        self.retriever = self.vector_store.get_retriever()
        self.memory = self.init_memory()
        self.chain = self.init_chain()

    def get_history(self) -> Dict:
        """get the history of conversation

        Returns:
            list: list of messages between AI and human
        """
        history = self.memory.load_memory_variables(inputs={"history"})

        return history

    def init_chain(self):
        prompt = PredefinedPrompt()
        self.ANSWER_PROMPT = prompt.ANSWER_PROMPT
        self.CONDENSE_QUESTION_PROMPT = prompt.CONDENSE_QUESTION_PROMPT

        generator = Generator(model_params=llm_config["model_params"])
        self.llm = generator.model

        self.output_parser = StrOutputParser()

        if self.use_retriever and self.use_chat_history:
            chain = self.get_conversional_chain()
        elif self.use_retriever and not self.use_chat_history:
            chain = self.get_retrieval_chain()
        else:
            chain = self.get_answer_chain()

        return chain

    def invoke(self, query: Union[QueryItem, QuestionItem]) -> Dict:
        """invoke the chain

        Args:
            query (Union[QueryItem, QuestionItem]): the input including question or a pair of question and context

        Returns:
            Dict: the answer of incoming query
        """
        answer = None
        answer = self.chain.invoke(query.model_dump())

        if not self.use_retriever or isinstance(answer, str):
            answer = {"answer": answer}

        logger.info(type(answer))
        # if self.memory:
        #     self.memory.save_context(query.model_dump(), {"answer": answer["answer"]})

        return answer

    def init_memory(self):
        """init the memory cache

        Returns:
            _type_: the memory object
        """
        memory = ConversationBufferMemory(
            return_messages=True, output_key="answer", input_key="question"
        )

        return memory

    def get_answer_chain(self):
        answer_chain = self.ANSWER_PROMPT | self.llm | self.output_parser

        return answer_chain

    def get_retrieval_chain(self):
        logger.info("get_retrieval_chain")
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=lambda x: x["context"])
            | self.ANSWER_PROMPT
            | self.llm
            | StrOutputParser()
        )

        chain = RunnableParallel(
            {
                "context": itemgetter("question")
                | self.retriever
                | self.vector_store._combine_documents,
                "question": itemgetter("question") | RunnablePassthrough(),
            }
        ).assign(answer=rag_chain_from_docs)

        return chain

    def get_conversional_chain(self):
        history = RunnablePassthrough.assign(
            chat_history=RunnableLambda(self.memory.load_memory_variables)
            | itemgetter("history"),
        )

        standalone_question = {
            "standalone_question": {
                "question": lambda x: x["question"],
                "chat_history": lambda x: (
                    ""
                    if self.use_chat_history
                    else get_buffer_string(x["chat_history"])
                ),
            }
            | self.CONDENSE_QUESTION_PROMPT
            | self.llm,
        }

        retrieved_documents = {
            "docs": itemgetter("standalone_question")
            | self.retriever
            | self.vector_store._combine_documents,
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

        chain = history | standalone_question | retrieved_documents | answer

        return chain
