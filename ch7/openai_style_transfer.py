# 引入套件
from openai import OpenAI
import base64
import os

# 影像檔
image_path = "images/chef.png"


# 建立用戶端物件
client = OpenAI()

# 定義函數將影像轉換為Base64格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 將影像轉換為Base64格式
base64_image = encode_image(image_path)

# 呼叫 API
response = client.responses.create(
    model="gpt-5.6-luna",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", 
                 "text": "依據你對我的所有了解，製作一張關於我和我工作的吉卜力風格誇張漫畫"
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
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
    os.makedirs("output", exist_ok=True)
    with open("output/吉卜力風格.png", "wb") as f:
        f.write(base64.b64decode(image_base64))