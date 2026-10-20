# pip install langchain-chroma python-magic-bin==0.4.14 langchain-ollama 
# 引入套件
import os
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# 文件分塊
loader = UnstructuredLoader('data/1.txt')
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
all_splits = text_splitter.split_documents(docs)
# 分成幾塊(Chunks)
print('塊數： ', len(all_splits))
print(all_splits)

# Chroma 只允許字串，但 split_documents 函數會產生 List，故修改languages值為字串
for index in range(len(all_splits)):
    all_splits[index].metadata['languages'] = 'zh'
        
# 使用 Ollama 載入詞嵌入模型
from langchain.embeddings import init_embeddings
embeddings = init_embeddings(model="qwen3-embedding", provider = 'ollama')

# 使用Chroma向量資料庫
vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

# 將所有區塊存入向量資料庫
id_list = [f'黃金_{index+1:0d}' for index, _ in enumerate(all_splits)]  
_ = vector_store.add_documents(ids=id_list, documents=all_splits)

# 顯示向量資料庫內容
result = vector_store.get()
print('向量資料庫內容:')
print(len(result['ids']))
print(result)

# 以文字進行相似度搜尋(Similarity Search)
query = "最新黃金價格=?"
results = vector_store.similarity_search(query, k=2, filter={"source": 'data/1.txt'})
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
    
# 更新第一個區塊內容
all_splits[0].page_content = '黃金突然大漲！衝上1週高點 關鍵推手曝光\n' +  all_splits[0].page_content
_ = vector_store.update_documents(ids=id_list[0], documents=[all_splits[0]])

# 刪除最後一個區塊
_ = vector_store.delete(ids=id_list[-1])

result = vector_store.get()
print('更新後內容:')
print(len(result['ids']))
print(result['documents'])    