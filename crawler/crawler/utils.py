import logging as logger
import os
import re
import sys
from functools import wraps
from hashlib import sha256
from typing import Any, AnyStr, Dict, List, Optional, Union

import yaml

from crawler.settings import CHUNKING_PROMPT, GEMINI_API

# import this near the top of the page
sys.path.append(os.path.join(os.path.abspath("../")))
from chatbot.embedd import EmbeddingModel
from configs.config import embedding_config


def check_spider_pipeline(process_item_method):
    """Decorator for checking pipeline scrapy

    Args:
        process_item_method (function): a function to check

    Returns:
        _type_: function to check pipeline scrapy is applied or not
    """

    @wraps(process_item_method)
    def wrapper(self, item, spider):
        # message template for debugging
        msg = "%%s %s pipeline step" % (self.__class__.__name__,)
        msg = f"{self.__class__.__name__} pipeline step"

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if self.__class__ in spider.pipeline:
            spider.logger.info(f"{msg} executing")
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            spider.logger.info(f"{msg} executing")
            return item

    return wrapper


class CleanText:
    """Clean text"""

    def __init__(self) -> None:
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+",
            flags=re.UNICODE,
        )

        self.remove_escape_character_pattern = re.compile(r"([\r|\n|\t|\xa0])+")

    def remove_emoji(self, text):
        return re.sub(self.emoji_pattern, " ", text)

    def remove_escape_character(self, text):
        text = re.sub(r"([\r|\t|\xa0])+", " ", text)
        text = re.sub(r"(\n)+", "\n", text)
        text = re.sub(r"(\s)+", " ", text)
        return text

    def clean_text(self, text):
        text = self.remove_emoji(text)
        text = self.remove_escape_character(text)

        return text

    def __call__(self, text, *args: Any, **kwargs: Any) -> Any:
        return self.clean_text(text=text)


def generate_id(title: AnyStr, date_range: AnyStr, url: AnyStr) -> AnyStr:
    """Generate id by using hash function of title, date_range, and url

    Args:
        title (AnyStr): Title of promotion
        date_range (AnyStr): promotion time
        url (AnyStr): url of promotion

    Returns:
        AnyStr: id of the promotion
    """
    text = url if url else ""
    text += title if title else ""
    text += date_range if date_range else ""
    return sha256(text.encode("utf-8")).hexdigest()


def extract_question_answer(
    data: AnyStr,
    question_answer_pair_split: AnyStr = "************",
    question_answer_split: AnyStr = "******",
):
    synthetic_data = []

    list_question_answer = data.split(question_answer_pair_split)
    for question_answer_pair in list_question_answer:
        if question_answer_pair:
            question_answer = question_answer_pair.split(question_answer_split)

            try:
                data = {}
                if len(question_answer) == 2 or len(question_answer) == 3:
                    question = question_answer[0].split(":", 1)[1]
                    data["question"] = question.strip()
                    answer = question_answer[1].split(":", 1)[1]
                    data["answer"] = answer.strip()
                if len(question_answer) == 3:
                    context = question_answer[2].split(":", 1)[1]
                    data["context"] = context.strip()

                if data:
                    synthetic_data.append(data)
            except Exception as e:
                print(e)
                print(question_answer)

    return synthetic_data


def extract_question(data: AnyStr, question_split: AnyStr = "******") -> List:
    """Extract questions from generated response

    Args:
        data (AnyStr): response from llm
        question_split (AnyStr, optional): split string. Defaults to "******".

    Returns:
        List: list of questions
    """
    data = data.split(question_split)
    result = []

    for d in data:
        if d:
            question = ""
            try:
                question = d.strip().split(":", 1)[1]
            except Exception as e:
                logger.error(f"extract_question: have no question to extract {e}")

            if question:
                result.append(str(question.strip()))

    return result


class ChunkDocument:
    """Chunk document by using LLM"""

    def __init__(self, text: AnyStr, pattern: AnyStr = r"(\d+\..*?)(?=\n\d+\.|\Z)"):
        self.text = text
        self.pattern = pattern

    def __call__(self, *args, **kwargs):
        input_text = self.text
        num_matches_threshold = kwargs.get("num_matches_threshold")
        matches = re.findall(self.pattern, self.text, re.DOTALL)
        if num_matches_threshold:
            if len(matches) > num_matches_threshold:
                chunks = [match.strip() for match in matches]
            else:
                chunks = [input_text]

        else:
            chunks = [match.strip() for match in matches]
            if not chunks:
                chunks = [input_text]

        return chunks


LLM_TYPE = {"gemini": "gemini-pro"}


class LLMAPI:
    """function to call LLM API"""

    def __init__(self, API_KEY: AnyStr = GEMINI_API, type: AnyStr = "gemini") -> None:
        self.API_KEY = API_KEY
        self.type = type

        if self.type == "gemini":
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.API_KEY)
                self.model = genai.GenerativeModel(LLM_TYPE[self.type])
            except ImportError as e:
                raise e

    async def ainvoke(self, text: AnyStr) -> AnyStr:
        response = self.model.generate_content(
            text,
        )

        if not response.text:
            for i in range(3):
                response = self.model.generate_content(
                    text,
                )

                if response.text:
                    break

        return response.text

    def invoke(self, text: AnyStr) -> AnyStr:
        response = self.model.generate_content(
            text,
        )

        if not response.text:
            for i in range(3):
                response = self.model.generate_content(
                    text,
                )

                if response.text:
                    break

        return response.text


def llm_chunking(text: AnyStr) -> List[AnyStr]:
    llm = LLMAPI(API_KEY=GEMINI_API, type="gemini")
    return llm.invoke(CHUNKING_PROMPT.format(text=text))


embedding_model = EmbeddingModel(params=embedding_config)


def embedd(text: Union[AnyStr, List]) -> List:
    """convert text to vector

    Args:
        text (Union[AnyStr, List]): incoming text

    Returns:
        List: list of float represented as vector if input is a string else return list of list float represented as a list of vector
    """
    vectors = []
    if isinstance(text, str):
        try:
            vectors = embedding_model.embed_query(text)
        except Exception as e:
            vectors = []
            logger.error(e)
    else:
        try:
            vectors = embedding_model.embed_documents(text)
        except Exception as e:
            vectors = []
            logger.error(e)

    return vectors
