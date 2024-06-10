from typing import Any, AnyStr, Dict


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
