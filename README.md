# VNPT Customer Service Chatbot

This project focuses on developing a customer care chatbot for VNPT using the Retrieval-Augmented Generation (RAG) architecture. The chatbot aims to enhance customer support by providing accurate and timely responses to user queries.

Key Features:
  * RAG Architecture: Combines the strengths of retrieval-based and generative models to deliver precise and contextually relevant answers.
  * Enhanced Customer Support: Efficiently handles a wide range of customer inquiries, reducing response time and improving user satisfaction.
  * Scalable and Reliable: Designed to manage high volumes of interactions while maintaining performance and accuracy.
  * Continuous Improvement: Leveraging user feedback and interaction data to refine and optimize responses over time.


The image below will outline the RAG architecture in this project which contains SimCSE, Vistral, BM-25 model for embedding, generating, and reranking, respectively
![All-Diagram-System Diagram drawio](https://github.com/tuantotti/customer-service-chatbot/assets/75234453/c9617b6a-5bfd-4140-9c8a-eac7293f00b5)

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
4. [Contributing](#contributing)
5. [License](#license)
6. [Acknowledgements](#acknowledgements)

## Installation

### [Docker][#docker]
First, you need to setup docker from [official website]([URL](https://www.docker.com/))

```bash
# Clone the repository
git clone https://github.com/your-username/project-name.git

# Navigate to the project directory
cd project-name

# Build project
docker build .
```
#### If you want to run this project on CPU or GPU
#### If you want to run this project on CPU:
```bash
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
```
####If you want to run this project on GPU:
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```
#### Finally, run this project
```bash
docker run -i -t vnpt-chatbot:latest /bin/bash
```
