# 引入套件
import os, asyncio
from agents import Agent, Runner, WebSearchTool
from dotenv import load_dotenv

# 載入組態檔，取得模型代碼
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立Agent物件
agent = Agent(
    name="Assistant",
    tools=[
        # 網路搜尋
        WebSearchTool()
    ],
)

# 執行工具函數
async def main(prompt):
    result = await Runner.run(agent, prompt)
    print(result.final_output)


# 測試
if __name__ == "__main__":
    prompt="目前台灣對等關稅是幾% ?"
    asyncio.run(main(prompt))    