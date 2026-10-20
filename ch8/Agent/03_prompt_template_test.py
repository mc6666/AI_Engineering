# 引入套件
from openai import OpenAI
from dotenv import load_dotenv
import os

# 讀取組態檔
load_dotenv('../.env')
MODEL_ID = os.getenv('MODEL_ID')

# 建立 OpenAI 用戶端
client = OpenAI()

# 呼叫API
response = client.responses.create(
    prompt={
        "id": "pmpt_6a9abe98774081949a1a1ff6c1ef7fa70e6b6ca1692c451d",
        "version": "1",
        "variables": {"poem_style": "haiku"},
    },
)

# 顯示回應
print(response.output_text)