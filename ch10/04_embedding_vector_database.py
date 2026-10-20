# 引入套件
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import numpy as np

# 測試文件
sentences = [
    "The weather is sunny today.",
    "It's a beautiful day outside.",
    "The stock market plummeted."
]

# 載入詞嵌入模型
embeddings = OllamaEmbeddings(
    model="qwen3-embedding",
    dimensions=1024,
)

# 將文件轉換為詞向量，儲存至向量資料庫
vectorstore = InMemoryVectorStore.from_texts(
    sentences,
    embedding=embeddings,
)

# 將向量資料庫設為檢索器
retriever = vectorstore.as_retriever()

# 檢索及生成
retrieved_documents = retriever.invoke("How about the weather today?")
print(retrieved_documents[0].page_content)

# 定義Cosine similarity函數
def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    return dot / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 自向量資料庫取得詞向量
embed_documents = vectorstore.store.items()
# print(embed_documents)
vectors = []
for id, vector in embed_documents:
    vectors.append(vector['vector'])

# 進行Cosine similarity相似性比較
similarity1 = cosine_similarity(vectors[0], vectors[1])
print("Cosine Similarity 1:", similarity1)

similarity2 = cosine_similarity(vectors[0], vectors[2])
print("Cosine Similarity 2:", similarity2)