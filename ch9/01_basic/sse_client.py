# 引入套件
import asyncio
from mcp import Client
from mcp.client.sse import sse_client

# 呼叫 MCP Server
async def main():
    url = "http://localhost:8000/mcp"
    async with Client(sse_client("http://localhost:8000/sse")) as client:
        # 列舉 MCP Server 的工具函數
        result = await client.list_tools()
        print("Available Tools:")
        print([tool.name + ' ' + tool.description for tool in result.tools])
            
        # 呼叫 MCP Server 的天氣預報工具函數
        result = await client.call_tool(
            "get_weather", {"latitude": 25, "longitude": 121})
        print(f'\n回應：\n氣溫為{result.structured_content['result']}度')
        
# 測試  
if __name__ == "__main__":
    asyncio.run(main())                    