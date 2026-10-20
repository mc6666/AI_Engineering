# 引入套件
from openai import OpenAI
import os, json, requests
from dotenv import load_dotenv

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立 OpenAI 用戶端
client = OpenAI()

# 加值營業稅(VAT)函數
def calculate_and_print_vat(amount, rate=0.05, is_inclusive=True):
    """計算並顯示 VAT 營業稅明細
    amount: 金額
    rate: 稅率（預設 5% 0.05）
    is_inclusive: 金額是否已含稅（True 為含稅，False 為未稅）
    """
    if is_inclusive:
        # 含稅價拆算
        total = amount
        before_vat = total / (1 + rate)
        vat_amount = total - before_vat
    else:
        # 未稅價計算含稅
        before_vat = amount
        vat_amount = before_vat * rate
        total = before_vat + vat_amount

    # 列印格式化結果
    result = "--- 營業稅 (VAT) 計算明細 ---\n"
    result += f"未稅金額 (Before VAT): {before_vat:,.2f}\n"
    result += f"營業稅額 (VAT {int(rate * 100)}%): {vat_amount:,.2f}\n"
    result += f"含稅總額 (Total):      {total:,.2f}"
    return result

# 定義自訂函數的規格
tools = [{
  "type": "function",
  "name": "calculate_and_print_vat",
  "description": "計算VAT並顯示未稅金額、營業稅額及含稅總額",
  "strict": True,
  "parameters": {
    "type": "object",
    "required": [
      "amount",
      "rate",
      "is_inclusive"
    ],
    "properties": {
      "amount": {
        "type": "number",
        "description": "Monetary amount to calculate VAT from"
      },
      "rate": {
        "type": "number",
        "description": "VAT rate to apply (e.g., 0.05 for 5%)"
      },
      "is_inclusive": {
        "type": "boolean",
        "description": "Whether input amount is tax-inclusive (True) or exclusive (False)"
      }
    },
    "additionalProperties": False
  },
  "output_schema": {
    "type": "string",
    "description": "A formatted VAT calculation summary"
  }
}]

# 提示
prompt = "若含稅金額為105元，計算VAT並顯示未稅金額、營業稅額及含稅總額"
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
        "output": json.dumps(result)
    })
print('最後結果：')
print(json.dumps(input_messages, indent=4))    

print('計算結果：')
print(json.loads(input_messages[0]["output"]))    
