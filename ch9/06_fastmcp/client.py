# https://gofastmcp.com/integrations/fastapi
# 引入套件
import asyncio
from fastmcp import Client

# 呼叫 MCP Server
async def main() -> None:
    url = "http://localhost:8000/mcp"
    async with Client(url) as client:
        result = await client.call_tool(
            name="add",
            arguments={"a": 100, "b": 50},
        )
        print(result, '\n')
        print(result.structured_content['result'])
        
# 測試  
if __name__ == "__main__":
    asyncio.run(main())                    