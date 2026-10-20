   
# 引入套件
import asyncio
from mcp import Client
from mcp.client import ClientRequestContext
from mcp.types import ElicitRequestParams, ElicitRequestURLParams, ElicitResult

# 誘導(Elicitation)的表單資訊收集
async def handle_elicitation(context: ClientRequestContext, params: ElicitRequestParams) -> ElicitResult:
    if isinstance(params, ElicitRequestURLParams):
        print(f"Open this link to continue: {params.url}")
    answer = input(params.message+'\n') 
    if answer.lower().startswith('y'):
        return ElicitResult(action="accept", content={"accept_alternative": True, "date": "2025-12-27"})
    else:
        return ElicitResult(action="decline", content={}) # or cancel
        
# 呼叫 MCP Server
async def main():
    url = "http://localhost:8000/mcp"
    async with Client(url,
        mode="legacy",
        elicitation_callback=handle_elicitation,
    ) as client:
        result = await client.call_tool("pay_deposit", {"booking_id": "1234"})
        print(f'\n回應：{result.content[0].text}')
        
# 測試  
if __name__ == "__main__":
    asyncio.run(main())                        