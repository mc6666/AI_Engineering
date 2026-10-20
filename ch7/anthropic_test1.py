# 引入套件
from anthropic import Anthropic

# 建立用戶端物件
client = Anthropic()

# 呼叫 API
message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "幫冰淇淋店寫撰寫三個口號",
        }
    ],
    model="claude-opus-5",
)

# 顯示回應
for block in message.content:
    if block.type == "text":
        print(block.text)