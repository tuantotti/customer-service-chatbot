class Generator:
    def __init__(self, model_params) -> None:
        self.model_params = model_params
        self.model_path = self.model_params["model_path"]
        self.model = self.get_model()

    def get_model(self):
        llm = None
        if self.model_path.endswith(".gguf"):
            from langchain_community.llms import LlamaCpp

            # Use llama-cpp-python library to load model
            llm = LlamaCpp(**self.model_params)

        return llm

    def invoke(self, messages):
        return self.model.invoke(messages)
