# customer-service-chatbot
## Install package
### Install llama.cpp library for python
- If you want to run on CPU:
```bash
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
```
- If you want to run on GPU:
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```
