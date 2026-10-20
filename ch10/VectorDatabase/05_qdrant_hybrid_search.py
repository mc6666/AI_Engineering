# 引入套件
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from langchain_core.documents import Document

# 詞嵌入模型設定參數
embeddings_model = "qwen3-embedding"
no_of_dimensions = 4096

# 測試資料
docs = [
    "This a list which containing sample documents.",
    "Keywords are important for keyword-based search.",
    "Document analysis involves extracting keywords.",
    "Keyword-based search relies on sparse embeddings.",
    "Understsnding document structure aids in keyword extraction.",
    "Efficient keyword extraction enhances search accuracy.",
    "Semacntic similarity improves document retrieval performance.",
    "Machine learning techniques can optimize keyword extraction methods."
]

# 轉換為 Document List
document_list = [Document(id=i, page_content=item) for i, item in enumerate(docs)]

# 使用 Ollama 載入詞嵌入模型
from langchain.embeddings import init_embeddings
embeddings = init_embeddings(model=embeddings_model, provider = 'ollama')

# 連線到本地 Qdrant 向量資料庫
client = QdrantClient("http://localhost:6333")

# 建立 Collection
collection_name = "my_collection2"
if client.collection_exists(collection_name):
    client.delete_collection(collection_name=collection_name)
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=no_of_dimensions, distance=Distance.COSINE),
    sparse_vectors_config={
        "isbn-bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)
    },
)

# 建立Qdrant向量資料庫連線
vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

# 將所有區塊存入向量資料庫
id_list = range(1, len(docs)+1)  
_ = vector_store.add_documents(ids=id_list, documents=document_list)

# 以文字進行相似度搜尋(Similarity Search)
query = "Natural language processing techniques enhances keyword extraction efficiency"
results = vector_store.similarity_search(query, k=5)
print('以文字進行相似度搜尋:')
for res in results:
    print(f"* {res.page_content}")
    
# 以相似度分數排序
results = vector_store.similarity_search_with_score(query, k=5)
# 依分數 (score) 進行降冪排序 (reverse=True)
sorted_docs = sorted(results, key=lambda x: x[1], reverse=True)
print('以相似度分數排序:')
for res, score in sorted_docs:
    print(f"* [score={score:3f}] {res.page_content}")
    
    
    
