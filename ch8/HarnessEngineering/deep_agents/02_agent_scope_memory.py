# 引入套件
from langchain_core.utils.uuid import uuid7
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore
from dotenv import load_dotenv
import os

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立記憶
store = InMemoryStore()  

# 建立AGENTS.md的記憶(Seed the memory file)
store.put(
    ("my-agent",),
    "/memories/AGENTS.md",
    create_file_data("""## Response style
                        - Keep responses professional.
                        """.replace('  ', '')),
)

# 建立skill.md的記憶
store.put(
    ("my-agent",),
    "/skills/langgraph-docs/SKILL.md",
    create_file_data("""---
        name: langgraph-docs
        description: Fetch relevant LangGraph documentation to 
                     provide accurate guidance.
        ---

        # langgraph-docs
        Use the fetch_url tool to read https://docs.langchain.com/llms.txt, 
        then fetch relevant pages.
        """.replace('  ', '')),
)

# 建立 backend 物件
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(namespace=lambda _rt: ("my-agent",)),
        "/skills/": StoreBackend(namespace=lambda _rt: ("my-agent",)),
    }
)

# 建立 Deep Agent 物件
agent = create_deep_agent(
    model="openai:" + MODEL_ID,
    memory=["/memories/AGENTS.md"],
    skills=["/skills/"],
    backend=backend,
    store=store,
)

# 提示
prompt_1 = {"role": "user", 
    "content": "Now I prefer the responses is humorous instead of professional. Remember that."}
prompt_2 = {"role": "user", "content": "how to land the moon"}

# Print the agent's response
def print_result(i, result):
    for item in result["messages"][-1].content:
        if item['type'] == 'text':
            print(f'回應{i}:')
            print(item['text'])

# 定義呼叫 API 的函數
def call_api(i, prompt):
    config = {"configurable": {"thread_id": str(uuid7())}}
    result = agent.invoke(
        {"messages": [prompt]},
        config=config,
    )
    print_result(i, result)

# 第一次呼叫 API：LLM會使用專業的口吻回應。
call_api(1, prompt_2)

# 第二次呼叫 API：要求LLM更改記憶，改變偏好為幽默的回應。
call_api(2, prompt_1)

# 第三次呼叫 API：問題與第一次呼叫 API一樣，但會得到幽默的回應。
call_api(3, prompt_2)

