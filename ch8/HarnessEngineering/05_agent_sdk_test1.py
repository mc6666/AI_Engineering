# 引入套件
from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv
import os, sys
import asyncio

# 讀取組態檔
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立 Agent 物件
agent = Agent(
    name="Assistant",
    model=MODEL_ID,
    # instructions="Reply very concisely.",
)

# 提示
prompt_1 = {"role": "user", "content": "請推薦一家台北最值得吃的平民美食"}
prompt_2 = {"role": "user", "content": "我在台北車站，如何搭捷運去?"}

# 建立 Session
session = SQLiteSession("美食推薦", db_path="db/conversations.db")

# 呼叫API
async def main():
    # 第一次呼叫 OpenAI API
    response = await Runner.run(
        agent,
        input=[prompt_1],
        session=session, # 指定Session物件
    )
    print('*第一次回應:', response.final_output)

    # 追問(Follow up)
    second_response = await Runner.run(
        agent,
        input=[prompt_2],
        session=session, # 指定Session物件
    )
    print('\n\n*追問的回應:', second_response.final_output)

    
# 測試
if __name__ == "__main__":
    asyncio.run(main())    