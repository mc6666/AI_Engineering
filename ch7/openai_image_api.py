# 引入套件
from openai import OpenAI
import base64

# 建立用戶端物件
client = OpenAI()

prompt = "生成Web概念的Infographics，右下角有一位年輕且可愛的講師"

result = client.images.generate(model="gpt-image-2.5-sunburst", prompt=prompt)

# 取得影像
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# 影像存檔
with open("otter.png", "wb") as f:
    f.write(image_bytes)