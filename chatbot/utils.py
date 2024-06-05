from typing import Any, AnyStr, Dict, List
from datetime import datetime
import re


class SingletonMeta(type):
    _instances = {}

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self not in self._instances:
            instance = super().__call__(*args, **kwds)
            self._instances[self] = instance

        return self._instances[self]


def generate_question_answer(
        llm,
        prompt,
        data: Dict,
        question_answer_pair_split: AnyStr = "************",
        question_answer_split: AnyStr = "******",
):
    synthetic_chain = llm | prompt
    response = synthetic_chain.invoke(data)
    synthetic_data = []

    list_question_answer = response.split(question_answer_pair_split)
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


def extract_date_from_str(date_str: AnyStr) -> List[datetime]:
    date_pattern = r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}"
    date_range_list = re.findall(date_pattern, date_str)
    date_range_list = [datetime.strptime(date, '%d/%m/%Y') for date in date_range_list if date]
    return date_range_list


def is_older(docs_1, docs_2):
    """Check whether docs_1 is older than docs_2 based on date_range

    Args:
        docs_1: the first documents
        docs_2: the second documents

    Returns:
        True if docs_1 is older than docs_2 else False
    """
    date_range1 = docs_1.metadata['metadata']['date_range']
    date_range2 = docs_2.metadata['metadata']['date_range']
    date_list_1 = extract_date_from_str(date_range1)
    date_list_2 = extract_date_from_str(date_range2)

    if not date_list_1:
        return False

    if not date_list_2:
        return False

    if date_list_1[0] < date_list_2[0]:
        return True

    return False


def filter_old_docs(docs):
    # same id --> same promotion but different chunks
    # same name --> remove old promotion
    latest_docs = {}
    for index, doc in enumerate(docs):
        metadata = doc.metadata
        metadata_json = metadata.get("metadata")
        if metadata_json:
            title = metadata_json.get("title", "")
            latest_doc = latest_docs.get(title, None)
            if latest_doc:
                is_old = is_older(latest_doc, doc)
                latest_docs[index] = doc if is_old else latest_doc
            else:
                latest_docs[index] = doc

    filtered_docs = []
    for index in latest_docs.keys():
        filtered_docs.append(docs[index])

    return filtered_docs
