# 引入套件
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 呼叫 MCP Server
async def main():
    server_params = StdioServerParameters(
        command="python", # or "node", "uvx", etc.
        args=["./server.py"],
        env=None
    )

    # 建立 stdio 通道(Pipe)
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 建立 session 
            await session.initialize()
            
            # 列舉 MCP Server 的工具函數
            result = await session.list_tools()
            print("Available Tools:")
            print([tool.name for tool in result.tools]) 
            
            # 呼叫 MCP Server 的天氣預報工具函數
            result = await session.call_tool(
                "get_weather", {"latitude": 25, "longitude": 121})
            print(f'\n回應：\n氣溫為{result.structured_content['result']}度')

# 測試  
if __name__ == "__main__":
    asyncio.run(main())                    