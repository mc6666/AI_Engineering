# 引入套件
from openai import OpenAI
import base64

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
response = client.responses.create(
    model="gpt-5.6-luna",
    input="生成Web概念的Infographics，右下角有一位年輕且可愛的講師",
    tools=[{"type": "image_generation"}],
)

# 取得影像
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

# 影像存檔
if image_data:
    image_base64 = image_data[0]
    with open("Web_Infographics.png", "wb") as f:
        f.write(base64.b64decode(image_base64))