# 引入套件
import re
import json, requests
from transformers import AutoProcessor, AutoModelForMultimodalLM

# 讀取組態檔
MODEL_ID = "google/gemma-4-E2B-it" 
# 其他模型："google/gemma-4-E2B-it", "google/gemma-4-E4B-it", 
#         "google/gemma-4-12B-it", "google/gemma-4-31B-it", "google/gemma-4-26B-A4B-it"
model = AutoModelForMultimodalLM.from_pretrained(MODEL_ID, dtype="auto", device_map="auto")
processor = AutoProcessor.from_pretrained(MODEL_ID)

# 定義天氣預報函數(get_weather)
def get_weather(location: str):
    (latitude, longitude) = get_latitude_longitude(location)
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast" + \
        f"?latitude={latitude}&longitude={longitude}&current=temperature_2m" + \
        ",wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data['current']['temperature_2m']

def get_latitude_longitude(location: str):
    """
    Gets latitude and longitude for a given location.

    Args:
        location: The city name, e.g. San Francisco
    """
    return (25.0478, 121.5320)

# 定義自訂函數(get_weather)的規格
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

# 提示
input_list = [{"role": "user", "content": "What is the weather in Taipei today?"}]

# 呼叫 API
text = processor.apply_chat_template(input_list, tools=tools, tokenize=False, add_generation_prompt=True)
inputs = processor(text=text, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=1280)
generated_tokens = out[0][len(inputs["input_ids"][0]):]
response = processor.decode(generated_tokens, skip_special_tokens=False)

# 顯示執行結果
# print(out)
print('API執行結果：\n' + response)

# 根據回應內的呼叫函數的名稱及參數值，執行函數
def extract_tool_calls(text):
    def cast(v):
        try: return int(v)
        except:
            try: return float(v)
            except: return {'true': True, 'false': False}.get(v.lower(), v.strip("'\""))

    return [{
        "name": name,
        "arguments": {
            k: cast((v1 or v2).strip())
            for k, v1, v2 in re.findall(r'(\w+):(?:<\|"\|>(.*?)<\|"\|>|([^,}]*))', args)
        }
    } for name, args in re.findall(r"<\|tool_call>call:(\w+)\{(.*?)\}<tool_call\|>", text, re.DOTALL)]

calls = extract_tool_calls(response)

# 呼叫 call_function，並整理執行結果
if calls:
    message = []
    results = [
        {"name": c['name'], "response": globals()[c['name']](**c['arguments'])}
        for c in calls
    ]

    message.append({
        "role": "assistant",
        "tool_calls": [
            {"function": call} for call in calls
        ],
        "tool_responses": results
    })
    print(json.dumps(message, indent=2))

if len(message) > 0:
    print(message[0]["tool_responses"][0]["response"])

