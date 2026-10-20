# 引入套件
import re
from openai import OpenAI

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
response = client.responses.create(
    model="gpt-5.6-luna",
    input="Generate Iris Classification code in Python",
)

# 顯示回應
print(response.output_text)

# 截取 Python 程式碼
code_blocks = re.findall(r"```[a-zA-Z]*\n([\s\S]*?)\n```", response.output_text)
with open('iris_classification.py', 'w', encoding='utf8') as f:
    f.write(code_blocks[0])