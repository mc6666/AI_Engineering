# 引入套件
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from dotenv import load_dotenv

# 載入組態檔，取得模型代碼
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')
# print(MODEL_ID)

# 下載網路新聞
url = "https://www.ithome.com.tw/news/170362"
loader = UnstructuredLoader(web_url=url)
docs = loader.load()

# 分塊(Chunking)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
all_splits = text_splitter.split_documents(docs)
print(all_splits)

# 此段內容與主題無關
print('分塊(Chunking):')
print(all_splits[11])

# 網路新聞內容
print('網路新聞內容:')
print(docs[0])

# 分成幾段(Chunks)、網路新聞字數
print('分成幾段(Chunks)、網路新聞字數:')
print(len(all_splits), len(docs[0].page_content))

# 將網路新聞存入向量資料庫
from langchain_core.vectorstores import InMemoryVectorStore

# 使用 OpenAI 詞嵌入模型
embeddings = OpenAIEmbeddings()
# 使用存於記憶體的向量資料庫
vector_store = InMemoryVectorStore(embeddings)
# 將分塊內容存入向量資料庫
vector_store.add_documents(documents=all_splits[:11])

# 定義函數，提供資訊檢索
def retrieve(question):
    # 語意搜尋
    retrieved_docs = vector_store.similarity_search(question)
    return retrieved_docs

# 定義函數，使用提示範本合併上下文(Context)及提示
def augment_prompt(query, context):
    prompt_prefix = "Answer the question based only on the following context, " 
    prompt = prompt_prefix + f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    return prompt

# 定義函數，進行 RAG 檢索、補強及生成
def generate(question):
    context = retrieve(question)
    docs_content = "\n\n".join(doc.page_content for doc in context)
    messages = augment_prompt(question, docs_content)
    print(messages)
    response = llm.invoke(messages)
    return response.content

# 建置 OpenAI ChatBot
llm = ChatOpenAI(model=MODEL_ID)

# 測試
question = "著作權法是否保護畫風?"
response = generate(question)
print(response)



