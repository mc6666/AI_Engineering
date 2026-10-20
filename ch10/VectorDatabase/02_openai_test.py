# pip install -U langchain-qdrant qdrant-client
# 引入套件
import os
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# OpenAIEmbeddings Constants
embeddings_model = "text-embedding-3-small"
# 1536 dimensions for text-embedding-3-small
# 3072 dimensions for text-embedding-3-large
no_of_dimensions = 1536

# 文件分塊
loader = UnstructuredLoader('data/1.txt')
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
all_splits = text_splitter.split_documents(docs)
# 分成幾塊(Chunks)
print('塊數： ', len(all_splits))
print(all_splits)

# Chroma 只允許字串，但 split_documents 函數會產生 List，故修改languages值為字串
# for index in range(len(all_splits)):
    # all_splits[index].metadata['languages'] = 'zh'
        
# 載入OpenAI詞嵌入模型
embeddings = OpenAIEmbeddings(model=embeddings_model)

# 連線到本地 Qdrant 向量資料庫
client = QdrantClient("http://localhost:6333")

# 建立 Collection
collection_name = "my_collection"
if client.collection_exists(collection_name):
    client.delete_collection(collection_name=collection_name)
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=no_of_dimensions, distance=Distance.COSINE),
)

# 建立Qdrant向量資料庫連線
vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

# 將所有區塊存入向量資料庫
id_list = [index+1 for index, _ in enumerate(all_splits)]  
_ = vector_store.add_documents(ids=id_list, documents=all_splits)

# 顯示向量資料庫內容
# result = vector_store.get()
result = client.retrieve(
    collection_name=collection_name,
    ids=id_list
)
print(result)


# 以文字進行相似度搜尋(Similarity Search)
from qdrant_client import models
query = "最新黃金價格=?"
results = vector_store.similarity_search(query, k=2, 
    filter=models.Filter(
        should=[
            models.FieldCondition(
                key="source",
                match=models.MatchValue(
                    value="data/1.txt"
                ),
            ),
        ]
    )
)

print('以文字進行相似度搜尋:')
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")
    
# 以詞向量進行相似度搜尋
results = vector_store.similarity_search_by_vector(
    embedding=embeddings.embed_query(query), k=1
)
print('以詞向量進行相似度搜尋:')
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")
    
