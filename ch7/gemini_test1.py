# 引入套件
from google import genai

# 建立用戶端物件
client = genai.Client()

# 呼叫 API
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="幫冰淇淋店寫撰寫三個口號"
)

# 顯示回應
print(interaction.output_text)