# 引入套件
from openai import OpenAI
from dotenv import load_dotenv
import os, sys

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立 OpenAI 用戶端
client = OpenAI()

# 提示
prompt_1 = {"role": "user", "content": "請推薦一家台北最值得吃的平民美食"}
prompt_2 = {"role": "user", "content": "我在台北車站，如何搭捷運去?"}

# 第一次呼叫 OpenAI API
response = client.responses.create(
    model=MODEL_ID,
    input=[prompt_1],
)
print('*第一次回應:', response.output_text)

# 追問(Follow up)
second_response = client.responses.create(
    model=MODEL_ID,
    input=[prompt_2],
    previous_response_id=response.id,
)
print('\n\n*追問的回應:', second_response.output_text)