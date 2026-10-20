# 引入套件
import asyncio
from mcp import Client
from mcp.client import ClientRequestContext
from mcp.types import ElicitRequestParams, ElicitResult

# 誘導(Elicitation)的表單資訊收集
async def handle_elicitation(context: ClientRequestContext, params: ElicitRequestParams) -> ElicitResult:
    answer = input(params.message+'\n') #'確定要刪除嗎(y/n)\n')
    if answer.lower().startswith('y'):
        return ElicitResult(action="accept", content={'ok':True})
    else:
        return ElicitResult(action="accept", content={'ok':False})
        
# 呼叫 MCP Server
async def main():
    url = "http://localhost:8000/mcp"
    async with Client(url, elicitation_callback=handle_elicitation) as client:
        # 呼叫 MCP Server 的天氣預報工具函數
        result = await client.call_tool(
            "delete_folder", {"path": "./tmp/project"})
        print(f'\n回應：{result.structured_content['result']}')
        
# 測試  
if __name__ == "__main__":
    asyncio.run(main())      
