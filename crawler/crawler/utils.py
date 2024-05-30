import re
from functools import wraps
from hashlib import sha256
from typing import Any, AnyStr, Dict, Optional


def check_spider_pipeline(process_item_method):
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


class ChunkDocument:
    def __init__(self, text: AnyStr, pattern: AnyStr = r'(\d+\..*?)(?=\n\d+\.|\Z)'):
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
