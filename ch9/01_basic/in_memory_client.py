# 引入套件
from mcp import Client
import asyncio
from server import mcp

# 呼叫 MCP Server
async def main():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_weather", {"latitude": 25, "longitude": 121})
        print(result.structured_content['result'])

# 測試  
if __name__ == "__main__":
    asyncio.run(main())                    