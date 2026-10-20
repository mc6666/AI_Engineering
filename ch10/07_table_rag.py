# 引入套件
import os
from openai import OpenAI
from dotenv import load_dotenv

# 載入組態檔，取得模型代碼
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立OpenAI用戶端物件
client = OpenAI()

# 上傳檔案至OpenAI雲端
file = client.files.create(
    file=open("pdf/利率表.pdf", "rb"),
    purpose="user_data"
)

# 建立向量資料庫(Vector store)
vector_store = client.vector_stores.create(
    name="knowledge_base"
)
print(vector_store.id)

# 將上傳的檔案存入向量資料庫
result = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file.id
)
print(result)

# 呼叫API查詢利率
response = client.responses.create(
    model=MODEL_ID,
    input="使用上傳檔案查詢華南銀行112/3/1的二年期定期存款利率",
    tools=[{
        "type": "file_search",
        "vector_store_ids":[vector_store.id]
    }]
)
print(response.output_text)

response = client.responses.create(
    model=MODEL_ID,
    input="使用上傳檔案查詢第一銀行112/8/1的二年期定期存款利率?",
    tools=[{
        "type": "file_search",
        "vector_store_ids":[vector_store.id]
    }]
)
print(response.output_text)

# 刪除OpenAI雲端檔案及向量資料庫
response = client.files.delete(file.id)
print(response)

response = client.vector_stores.delete(vector_store.id)
print(response)



