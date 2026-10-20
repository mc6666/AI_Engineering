# 引入套件
import asyncio
from fastmcp import Client

# 設定 MCP Server 的 URL
url = "http://localhost:8000/mcp"

# 讀取 Access token
access_token = open('access_token.txt', encoding = 'utf8').read()

# 呼叫 MCP Server
async def main():
    async with Client(url, auth=access_token) as client:
        # 列舉 MCP Server 的工具函數
        result = await client.list_tools()
        print("Available Tools:")
        print([tool.name + ': ' + tool.description for tool in result])
            
        # 呼叫 MCP Server 的工具函數
        result = await client.call_tool(
            "roll_dice", {"n_dice": 3})
        print(f'\n回應：\n{result.data}')
        
# 測試  
if __name__ == "__main__":
    asyncio.run(main())                    