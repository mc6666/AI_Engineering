# 引入套件
from langchain_core.utils.uuid import uuid7
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
# from deepagents.backends.filesystem import FilesystemBackend
from langgraph.store.memory import InMemoryStore
from dotenv import load_dotenv
import os
from dataclasses import dataclass

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 設定常數
MEMORY = "/memories/"
AGENTS_FILE = MEMORY + "AGENTS.md"
SKILLS = "/skills/"
SKILL_FILE = "SKILL.md"

# 定義 MemoryContext，記錄使用者帳號及組織代碼
@dataclass(frozen=True)
class MemoryContext:
    user_id: str = "bob"
    # org_id: str = "default-org"

# 建立記憶
store = InMemoryStore()  

# 建立通用的AGENTS.md的記憶
namespace = ("my-agent",)
store.put(
    namespace,
    AGENTS_FILE,
    create_file_data("## 偏好: 使用中文註解"),
    # create_file_data("## Preferences: Likes detailed, narrative explanations"),
    # create_file_data("## Preferences: Python examples, without inline comment"),
    )
    
# 建立SKILL.md的記憶
store.put(
    ("alice",),
    SKILLS + "calculator/" + SKILL_FILE,
    create_file_data("""---
        name: calculator
        description: calculator spec
        ---
        include arithmetic operators ONLY.
        """.replace('  ', '')),
)

store.put(
    ("bob",),
    SKILLS + "calculator/" + SKILL_FILE,
    create_file_data("""---
        name: calculator
        description: calculator spec
        ---
        include arithmetic and scientific operators.  
        """.replace('  ', '')),
)

# 取得使用者帳號 
def user_namespace(rt):
    if rt.server_info and rt.server_info.user:
        return (rt.server_info.user.identity,)
    user_id = getattr(rt.context, "user_id", "alice")
    print(f'** user_id:{user_id}')
    return (user_id,)


# get org_id from namespace 
# def org_namespace(rt):
    # org_id = getattr(rt.context, "org_id", "unknown org")
    # print(f'** org_id:{org_id}')
    # return (org_id,)
    
# 建立 backend 物件
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        MEMORY: StoreBackend(namespace=lambda rt: namespace), 
        SKILLS: StoreBackend(namespace=lambda rt: user_namespace(rt)),
    }
)

# backend = FilesystemBackend(root_dir="./my-project")


# 建立 Deep Agent 物件
agent = create_deep_agent(
    model="openai:" + MODEL_ID,
    memory=[AGENTS_FILE],
    skills=[SKILLS],    
    context_schema=MemoryContext,
    backend=backend,
    store=store,
)

# 提示
prompt = {"role": "user", 
"content": "generator calculator based on AGENTS.md and SKILL.md"}
# "content": "按照使用者偏好，說明'如何製作蛋糕'"}
# "content": "按照使用者偏好，撰寫一個函數計算圓面積."}
# "content": "generate code for Machine Learning IRIS classification."}

# Print the agent's response
def print_result(i, result):
    for item in result["messages"][-1].content:
        if item['type'] == 'text':
            print(f'回應{i}:')
            print(item['text'])

# 定義呼叫 API 的函數
def call_api(i, user, prompt): #, org_id
    config = {"configurable": {"thread_id": str(uuid7())}}
    result = agent.invoke(
        {"messages": [prompt]},
        context=MemoryContext(user_id=user), #, org_id=org_id),
        config=config,
    )
    print_result(i, result)

# 第一次呼叫 API
call_api(1, 'alice', prompt) #, 'TSMC'

# 第二次呼叫 API
call_api(2, 'bob', prompt) #, 'HTC'

# saved = store.get(("bob",), "/memories/preferences.md")
# content = saved.value["content"]
# print("bob 的偏好：", content)