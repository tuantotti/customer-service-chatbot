from operator import itemgetter
from typing import Dict, Union, List
from langchain_core.documents import Document
import re
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from pyvi.ViTokenizer import tokenize
from chatbot.utils import filter_old_docs

from chatbot.embedd import EmbeddingModel
from chatbot.generator import Generator
from chatbot.prompts import PredefinedPrompt
from chatbot.reranker import BM25RerankerImpl
from chatbot.retriever import VectorStore
from chatbot.utils import SingletonMeta
from configs.config import llm_config
from rest_api.schemas.items import AnswerItem, QueryItem, QuestionItem
from utils.logger import Logger

logger = Logger.get_logger()


class CustomerServiceChatbot(metaclass=SingletonMeta):
    def __init__(self, use_retriever=True, use_chat_history=False) -> None:
        """Initial params

        Args:
            use_retriever (bool, optional): this flag checks whether using retriever model. Defaults to False.
        """
        self.output_parser = None
        self.retriever = None
        self.vector_store = None
        self.embedding_model = None
        self.llm = None
        self.generator = None
        self.CONDENSE_QUESTION_PROMPT = None
        self.ANSWER_PROMPT = None
        self.use_retriever = use_retriever
        self.use_chat_history = use_chat_history
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

        self.generator = Generator(model_params=llm_config["model_params"])
        self.llm = self.generator.model

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(embedding_model=self.embedding_model.model)
        self.retriever = self.vector_store.get_retriever()

        self.output_parser = StrOutputParser()

        if self.use_retriever and self.use_chat_history:
            chain = self.get_conversational_chain()
        elif self.use_retriever and not self.use_chat_history:
            chain = self.get_retrieval_chain()
        else:
            chain = self.get_answer_chain()

        return chain

    def invoke(self, query: Union[QueryItem, QuestionItem]) -> AnswerItem:
        """invoke the chain

        Args:
            query (Union[QueryItem, QuestionItem]): the input including question or a pair of question and context

        Returns:
            Dict: the answer of incoming query
        """
        answer = self.chain.invoke(query.model_dump())

        if not self.use_retriever or isinstance(answer, str):
            answer = {"answer": answer}

        # if self.memory:
        #     self.memory.save_context(query.model_dump(), {"answer": answer["answer"]})
        logger.info(answer)
        answer = self.post_process_answer(answer)
        answer_item = AnswerItem(
            question=answer.get("question", ""),
            context=answer.get("context", []),
            raw_context=answer.get("raw_context", []),
            docs=answer.get("docs", []),
            answer=answer.get("answer", ""),
            is_continue=answer.get("is_continue", False),
        )

        return answer_item

    @classmethod
    def post_process_answer(cls, answer):
        hard_additional_answer = (
            "Quý khách vui lòng để lại số điện thoại để đội ngũ chăm sóc khách hàng VNPT Money "
            "hỗ trợ."
        )
        answer['answer'] = answer['answer'].strip()
        if answer["context"]:
            metadata = answer["context"][0].metadata
            metadata_json = metadata.get("metadata")
            if metadata_json:
                url = metadata_json["url"]
                hard_additional_answer = (
                    f" Để biết thêm thông tin chi tiết, quý khách vui lòng truy cập đường link "
                    f"sau: {url}"
                )
                hard_additional_answer = hard_additional_answer if url else ""

        link_pattern = r'(https?://[^\s]+)'
        links = re.findall(link_pattern, answer['answer'])
        if answer["answer"].endswith("."):
            answer["answer"] = answer['answer'] + hard_additional_answer if len(links) < 1 else answer['answer']
        else:
            answer["is_continue"] = True

        return answer

    @classmethod
    def init_memory(cls):
        """init the memory cache

        Returns:
            _type_: the memory object
        """
        memory = ConversationBufferWindowMemory(
            return_messages=True, output_key="answer", input_key="question", k=2
        )

        return memory

    def get_answer_chain(self):
        answer_chain = self.ANSWER_PROMPT | self.llm | self.output_parser

        return answer_chain

    def get_retrieval_chain(self):
        query = RunnablePassthrough.assign(question=lambda x: x["question"])
        retrieved_documents = {
            "question": itemgetter("question"),
            "docs": itemgetter("question") | RunnableLambda(tokenize) | self.retriever,
        }

        final_inputs = {
            "question": itemgetter("question"),
            "context": lambda x: self.post_process_retrieval(x["question"], x["docs"]),
        }

        output = {
            "question": itemgetter("question"),
            "docs": itemgetter("docs"),
            "raw_context": final_inputs["context"],
            "context": final_inputs["context"],
            "answer": final_inputs
                      | RunnableLambda(self.combine)
                      | self.ANSWER_PROMPT
                      | self.llm
                      | StrOutputParser(),
        }

        chain = query | retrieved_documents | output

        return chain

    def post_process_retrieval(self, question, docs):
        reranked_docs = []
        if docs:
            reranked_docs = self.reranking(question, docs)
        if reranked_docs:
            reranked_docs = filter_old_docs(reranked_docs)
        return reranked_docs

    @classmethod
    def reranking(cls, question, docs) -> List[Document]:
        reranker = BM25RerankerImpl.from_documents(docs, k=4)
        reranked_docs = reranker.invoke(question)

        return reranked_docs

    def combine(self, final_inputs):
        final_inputs["context"] = self.vector_store._combine_documents(
            final_inputs["context"]
        )

        return final_inputs

    def get_conversational_chain(self):
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
            "question": itemgetter("question"),
            "context": final_inputs["context"],
            "answer": final_inputs | self.ANSWER_PROMPT | self.llm,
        }

        chain = history | standalone_question | retrieved_documents | answer

        return chain
