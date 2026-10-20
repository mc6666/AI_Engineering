# 引入套件
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

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
embeddings = init_embeddings(model="qwen3-embedding", provider = 'ollama')

# 使用Chroma向量資料庫
vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db2",
)

# 將所有區塊存入向量資料庫
id_list = [f'{index+1:0d}' for index, _ in enumerate(document_list)]  
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
    
# 以BM25重新排序
from rank_bm25 import BM25Okapi
tokenized_corpus = [doc.split(" ") for doc in docs]
bm25 = BM25Okapi(tokenized_corpus)
tokenized_query = query.split(" ")
doc_scores = bm25.get_scores(tokenized_query)
results = []
for doc in zip(docs, doc_scores):
    results.append(doc)
sorted_docs = sorted(results, key=lambda x: x[1], reverse=True)
print('\n以BM25重新排序:')
for res, score in sorted_docs:
    print(f"* [score={score:3f}] {res}")
