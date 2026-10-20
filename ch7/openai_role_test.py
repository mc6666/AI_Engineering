# 引入套件
from openai import OpenAI

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
response = client.responses.create(
    model="gpt-5.6-luna",
    input=[
        {"role": "system", "content": "你是廣告行銷專家"},
        {
            "role": "user",
            "content": "幫冰淇淋店寫撰寫三個口號",
        },
    ],
)

# 顯示回應
print(response.output_text)