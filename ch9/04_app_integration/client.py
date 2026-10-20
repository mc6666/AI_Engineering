# https://py.sdk.modelcontextprotocol.io/run/asgi/#mounting-it
# 引入套件
import asyncio
from mcp import Client

# 呼叫 MCP Server
async def main():
    url = "http://localhost:8000/mcp"
    async with Client(url) as client:
        # 呼叫 MCP Server 的工具函數
        result = await client.call_tool(
            "add_note", {"text":"台北的緯度(Latitude):25, 經度(Longitude): 121"})
		# 完整的JSON字串        
        print(result, '\n')
		# 解析的回應
        print(result.structured_content['result'])
        return result
        
# 測試  
if __name__ == "__main__":
    asyncio.run(main())                    