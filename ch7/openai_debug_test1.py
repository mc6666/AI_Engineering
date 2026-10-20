# 引入套件
from openai import OpenAI

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
response = client.responses.create(
    model="gpt-5.6-luna",
    input="""Find the null pointer exception in this code:

def display_name(user):
    return user.profile.name

print(display_name(None))
""",
    reasoning={"effort": "low"},
)

# 顯示回應
print(response.output_text)