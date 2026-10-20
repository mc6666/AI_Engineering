from langchain_openai.chat_models import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.retrievers import BM25Retriever
import os 
from dotenv import load_dotenv
from langchain import hub

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')
db_file_path=os.getenv('VECTOR_STORE_PATH')
# embeddings = HuggingFaceEmbeddings()
Embeddings_Model = os.getenv('EMBEDDING_MODEL')

# 使用 Ollama 詞嵌入模型
embeddings = OllamaEmbeddings(model=Embeddings_Model)

# 載入向量資料庫
db = None
if os.path.exists(db_file_path):
    db = FAISS.load_local(db_file_path, embeddings=embeddings
                               , allow_dangerous_deserialization=True)
def creation_of_vectorDB_in_local(loader):
    global db
    data = loader.load()
    if db is None:
        db =FAISS.from_documents(data, embeddings)
    else:
        db.add_documents(data)
    db.save_local(db_file_path)

# 定義RAG查詢的函數
def creation_FAQ_chain(query):
    retriever = db.as_retriever(score_threshold=0.7, k=3)
    
    llm = ChatOpenAI(model=MODEL_ID)
    
    # 適合問答(question-answering)的提示
    system_prompt = (
    "Use the given context to answer the question. "
    "If the answer is not found in the context, kindly state 'This Question not Present in My Database.' "
    "Use three sentence maximum and keep the answer concise. "
    "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # 定義問答的鏈結(chain)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    # 執行鏈結(chain)
    response = chain.invoke({"input": query})

    # 顯示執行結果
    print('-'*100)
    print(f'QUERY：{query}\n')
    response_head = 'response: '
    prompt_head = 'Prompt: '
    for item in response['context']:
        print(item.page_content, '\n')
    index = response['context'][0].page_content.find(response_head)
    if index < 0:
        return response['context'][0].page_content
    else:
        # 找出FAQ的Prompt欄位
        docs = []
        for item in response['context']:
            index2 = item.page_content.find(response_head)
            if index2 >= 0:
                docs.append(Document(page_content=
                    item.page_content[len(prompt_head):index2]))
                
        # reranking: 以 BM25 比較查詢與FAQ的Prompt欄位，找出最佳答案
        retriever = BM25Retriever.from_documents(docs, k=1)
        result = retriever.invoke(query)
        for item in response['context']:
            if result[0].page_content in item.page_content:
                index = item.page_content.find(response_head)
                return item.page_content[index+len(response_head):]
        else:
            return response['context'][0].page_content[index+len(response_head):]
