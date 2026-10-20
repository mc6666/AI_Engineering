# 引入套件
import asyncio
from openai import OpenAI
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings

# 設定 MCP Server 的 URL
url = 'http://locahost:8000/mcp'

# 讀取 Access token
access_token = open('access_token.txt', encoding = 'utf8').read()
# print(f"Access token:\n{access_token}")

# 測試  
async def run(agent:Agent, message:str):
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

# 連接 MCP Server，建立 Agent 物件
async def main():
    # 連接 MCP Server 
    url = "http://localhost:8000/mcp"
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={
            "url": url,
            "headers": {
                "Authorization": f"Bearer {access_token}"
            }
        },
    ) as server:
        # 建立 Agent 物件
        agent = Agent(
            name="Assistant",
            instructions="Use the tools to answer the questions.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required"),
        )
        
        # 測試        
        message = "roll_dice 2 times"
        trace_id = gen_trace_id()
        with trace(workflow_name="Authentication Agent", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/logs/trace?trace_id={trace_id}\n")
            await run(agent, message)

# 啟動 Agent  
if __name__ == "__main__":
    asyncio.run(main())
