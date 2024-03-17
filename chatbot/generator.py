from configs.config import llm_config


class Generator:
    def __init__(self, is_hf_model=False) -> None:
        self.is_hf_model = is_hf_model
        self.generator = self.get_model()

    def get_model(self):
        llm = None
        if self.is_hf_model == False:
            from langchain_community.llms import LlamaCpp

            # Use llama-cpp-python library to load model
            llm = LlamaCpp(llm_config)

        return llm

    def invoke(self, messages):
        return self.generator.invoke(messages)
