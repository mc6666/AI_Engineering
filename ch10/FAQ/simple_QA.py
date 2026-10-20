# 引入套件
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_unstructured import UnstructuredLoader
from langchain_core.documents import Document
from dotenv import load_dotenv
import os, sys

# 常數設定
embeddings_model = "qwen3-embedding"
no_of_dimensions = 4096
VECTOR_STORE_PATH='vector_store'
DOCUMENT_PATH='./data/Amazon_EC2_FAQ.csv'

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 使用 Ollama 載入詞嵌入模型
from langchain.embeddings import init_embeddings
embeddings = init_embeddings(model=embeddings_model, provider = 'ollama')

# 連線到本地 Qdrant 向量資料庫
client = QdrantClient("http://localhost:6333")

# 建立 Collection
collection_name = "my_collection3"
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

# 讀取檔案
docs = open(DOCUMENT_PATH, encoding='utf8').readlines()
# 轉換為 Document List
document_list = [Document(id=i, page_content=item) for i, item in enumerate(docs)]

# 將所有文件存入向量資料庫
# loader = UnstructuredLoader(DOCUMENT_PATH)
# document_list = loader.load()
id_list = range(1, len(docs)+1)  
_ = vector_store.add_documents(ids=id_list, documents=document_list)

# 建立檢索器(retriever)
# retriever = vector_store.as_retriever(search_kwargs={"k": 1})

# 定義提示範本(prompt template)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful RAG assistant.
            Answer the user's question using ONLY the supplied context.
            If the answer cannot be found in the context, say:
            "I don't have enough information in the provided documents."
            Do not invent facts.
            Include source references when possible.
            """.replace('  ', '')
        ),
        (
            "human",
            """
            Context:
            {context}

            Question:
            {question}
            """.replace('  ', '')
        ),
    ]
)

# 建立 ChatOpenAI
llm = ChatOpenAI(model=MODEL_ID, temperature=0)

# 測試
while True:
    # question = "如何使用 Amazon EC2"
    question = input("What is your question?\n")
    if len(question) == 0:
        break
        

    # 以文字進行相似度搜尋(Similarity Search)
    results = vector_store.similarity_search(question, k=1)
    # print('以文字進行相似度搜尋:')
    context=''
    for res in results:
        # print(f"* {res.page_content}")
        context += res.page_content + '\n'
    
    # 呼叫 ChatOpenAI，取得回應
    chain = prompt | llm
    response = chain.invoke(
        {
            "context": context, # retriever,
            "question": question,
        }
    )
    print(response.content)