from huggingface_hub import hf_hub_download
import os

base_path = "output/llm/"
if not os.path.exists(directory):
    os.makedirs(base_path)

model_id = "Viet-Mistral/Vistral-7B-Chat"
hf_hub_download(
    repo_id=model_id, 
    filename="ggml-vistral-7B-chat-q4_0.gguf", 
    local_dir=f"{base_path}/ggml-vistral-7B-chat-q4_0.gguf"
)
