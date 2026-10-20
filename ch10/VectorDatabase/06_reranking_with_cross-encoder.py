# !pip install -qU sentence_transformers 
# 引入套件
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

# 測試文件
document_1 = Document(
    page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)

document_2 = Document(
    page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
    metadata={"source": "news"},
)

document_3 = Document(
    page_content="I will go shopping tomorrow if weather is sunny. I will  stay home if tomorrow weather is cloudy or raining.",
    metadata={"source": "tweet"},
)

document_4 = Document(
    page_content="Robbers broke into the city bank and stole $1 million in cash.",
    metadata={"source": "news"},
)

document_5 = Document(
    page_content="Wow! That was an amazing movie. I can't wait to see it again.",
    metadata={"source": "tweet"},
)

document_6 = Document(
    page_content="Is the new iPhone worth the price? Read this review to find out.",
    metadata={"source": "website"},
)

document_7 = Document(
    page_content="The top 10 soccer players in the world right now.",
    metadata={"source": "website"},
)

document_8 = Document(
    page_content="LangGraph is the best framework for building stateful, agentic applications!",
    metadata={"source": "tweet"},
)

document_9 = Document(
    page_content="The stock market is down 500 points today due to fears of a recession.",
    metadata={"source": "news"},
)

document_10 = Document(
    page_content="I have a bad feeling I am going to get deleted :(",
    metadata={"source": "tweet"},
)

documents = [
    document_1,
    document_2,
    document_3,
    document_4,
    document_5,
    document_6,
    document_7,
    document_8,
    document_9,
    document_10,
]

# 顯示文件
for doc in documents:
    print(doc.page_content)

# 使用 Ollama 載入詞嵌入模型qwen3-embedding
from langchain.embeddings import init_embeddings
embeddings = init_embeddings(model="qwen3-embedding", provider = 'ollama')

# 將提示與測試文件配對
query = "tomorrow weather" # 提示
pairs = [(query, doc.page_content) for doc in documents]

# 以 Cross-encoder 比對提示與測試文件
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
scores = cross_encoder.predict(pairs)

# 排序
ranked_documents = [(score, doc) for score, doc in 
                    sorted(zip(scores, documents), reverse=True)]
                          
# 顯示比對結果 
for score, doc in ranked_documents:
    print(f"* [score={score:3f}] {doc.page_content}")



