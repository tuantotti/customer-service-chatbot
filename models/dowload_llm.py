from huggingface_hub import snapshot_download

model_id = "Viet-Mistral/Vistral-7B-Chat"

snapshot_download(
    repo_id=model_id,
    local_dir="output/Vistral-7B-Chat-HF",
    token="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",
    local_dir_use_symlinks=False,
    revision="main",
)
