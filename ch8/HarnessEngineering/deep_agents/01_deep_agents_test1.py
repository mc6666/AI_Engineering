# 引入套件
from deepagents import create_deep_agent
from dotenv import load_dotenv
import os


# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# OpenAI 內建的 Web search 工具函數
internet_search = {"type": "web_search"}

# 建立 Deep Agent 物件
research_instructions = '請使用網路搜尋工具作為獲取資訊的主要手段'
agent = create_deep_agent(
    model=MODEL_ID,
    tools=[internet_search], # 導入 Web search 工具函數
    system_prompt=research_instructions,
)

# 提示
prompt = {"role": "user", "content": "What is Deep Agents?"}

# 呼叫 API
result = agent.invoke({"messages": [prompt]})

# Print the agent's response
for item in result["messages"][-1].content:
    if item['type'] == 'text':
        print('回應:\n', item['text'])
