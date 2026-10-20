# 引入套件
from openai import OpenAI
import base64
import os

# 影像檔
image_path = "images/chef.png"


# 建立用戶端物件
client = OpenAI()

# 定義函數將影像上傳
def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(file=file_content, purpose="vision")
    return result.id

# 取得上傳影像的ID
fileId = create_file(image_path)

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
                    "file_id": fileId,
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