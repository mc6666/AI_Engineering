# 引入套件
from langchain.embeddings import init_embeddings
import numpy as np

# 測試文件
sentences = [
    "The weather is sunny today.",
    "It's a beautiful day outside.",
    "The stock market plummeted."
]

# 詞嵌入，將文件轉換為詞向量
model = init_embeddings(model="qwen3-embedding", provider = 'ollama')
vectors = model.embed_documents(sentences)
# print(vectors)

# 定義Cosine similarity函數
def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    return dot / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 進行Cosine similarity相似性比較
similarity1 = cosine_similarity(vectors[0], vectors[1])
print("Cosine Similarity 1:", similarity1)

similarity2 = cosine_similarity(vectors[0], vectors[2])
print("Cosine Similarity 2:", similarity2)