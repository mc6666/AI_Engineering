# 引入套件
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from dotenv import load_dotenv
import os

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立 Agent 物件
agent = create_agent(
    model=MODEL_ID,
    checkpointer=InMemorySaver(),
)

# 提示
prompt_1 = {"role": "user", "content": "請推薦一家台北最值得吃的平民美食"}
prompt_2 = {"role": "user", "content": "我在台北車站，如何搭捷運去?"}

# 呼叫API
thread_config = {"configurable": {"thread_id": "1"}}
response = agent.invoke(
    {"messages": [prompt_1]},
    thread_config,
)
print('第一次回應:')
print(response["messages"][-1].content)

# 追問(Follow up)
second_response = agent.invoke(
    {"messages": [prompt_2]},
    thread_config,
)
print('\n*追問的回應:', second_response["messages"][-1].content)
