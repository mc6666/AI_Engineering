# pip install -U langgraph-checkpoint-postgres "psycopg[binary]"
# 引入套件
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver  
from dotenv import load_dotenv
import os

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 提示
prompt_1 = {"role": "user", "content": "Hi! My name is Bob."}
prompt_2 = {"role": "user", "content": "What's my name?"}

# 建立 Agent 物件
DB_URI = "postgresql://test:1234@localhost:5432/agent_db?sslmode=disable"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup() # auto create tables in PostgreSQL
    agent = create_agent(
        model=MODEL_ID,
        checkpointer=checkpointer,
    )

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
    print('\n*追問的回應:')
    print(second_response["messages"][-1].content)
