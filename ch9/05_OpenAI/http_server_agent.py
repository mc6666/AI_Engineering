# 引入套件
import asyncio
import sys, os, subprocess, time
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings

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
        message = "請提供台北今天氣溫"
        trace_id = gen_trace_id()
        with trace(workflow_name="Agent using Streamable HTTP MCP", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/logs/trace?trace_id={trace_id}\n")
            await run(agent, message)

# 啟動 MCP Server 及 Agent  
if __name__ == "__main__":
    # 啟動本機的 MCP Server
    this_dir = os.path.dirname(os.path.abspath(__file__))
    server_file = os.path.join(this_dir, "http_server.py")
    process = subprocess.Popen(["python", server_file])
    # Give it 2 seconds to start
    time.sleep(2)

    try:
        # 啟動 Agent
        asyncio.run(main())
    finally:
        # 程式結束時關閉 MCP Server
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
