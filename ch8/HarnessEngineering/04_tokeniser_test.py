# pip install tiktoken
# 引入套件
import tiktoken

# 提示
prompt = "請推薦一家台北最值得吃的平民美食"

# 取得OpenAI模型對應的分詞器(Tokeniser)
enc = tiktoken.encoding_for_model("gpt-5.6-luna")

# 分詞
encode = enc.encode(prompt)
print('分詞的長度:', len(encode))
