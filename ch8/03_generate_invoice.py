# 引入套件
from openai import OpenAI
import os, json, requests
from dotenv import load_dotenv
from TaiwanInvoiceClass import *

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立 OpenAI 用戶端
client = OpenAI()

# 加值營業稅(VAT)函數

# 載入工具函數的定義
with open('invoice_function_spec.json', 'r', encoding='utf-8') as f:
    tools = [json.load(f)]

# 載入提示
prompt = open('03_prompt.txt', encoding='utf8').read()
input_list = [{"role": "user", "content": prompt}]

# 呼叫API
response = client.responses.create(
    model=MODEL_ID, # 模型
    tools=tools,        # 指定函數
    input=input_list,   # 提示
)

# 顯示執行結果
# print('API執行結果：\n' + response.model_dump_json(indent=2))

# 根據回應內的呼叫函數的名稱及參數值，執行函數
def call_function(function_name, args):
    # print(function_name)
    return globals()[function_name](**args)

# 呼叫 call_function，並整理執行結果
input_messages = []
for tool_call in response.output:
    if tool_call.type != "function_call":
        continue

    # 解析OpenAI API的回應
    name = tool_call.name
    args = json.loads(tool_call.arguments)

    # 根據解析結果呼叫函數
    result = call_function(name, args)
    input_messages.append({
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": result
    })
print('輸出檔案路徑：')
print(input_messages[0]["output"])   
