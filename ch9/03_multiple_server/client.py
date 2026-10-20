# 引入套件
import asyncio
from mcp import ClientSessionGroup, StdioServerParameters
from mcp.types import Implementation, TextResourceContents

# 以 MCP Server 名稱區分工具函數
def by_server(name: str, server_info: Implementation) -> str:
    return f"{server_info.name}.{name}"
    
# 呼叫 MCP Server
async def main() -> None:
    # 以 uv 啟動 MCP Server 的指令集參數
    # library = StdioServerParameters(command="uv", args=["run", "mcp", "run", "library_server.py"])
    # web = StdioServerParameters(command="uv", args=["run", "mcp", "run", "web_server.py"])
    
    # 以 mcp 啟動 MCP Server 的指令集參數
    library = StdioServerParameters(command="mcp", args=["run", "library_server.py"])
    library2 = StdioServerParameters(command="mcp", args=["run", "library_server2.py"])
    web = StdioServerParameters(command="mcp", args=["run", "web_server.py"])

    # 建立 MCP Server Group
    async with ClientSessionGroup() as group:
        session_library2 = await group.connect_to_server(library2)
        session_web = await group.connect_to_server(web)

        # 呼叫 MCP Server 工具函數
        result = await group.call_tool("search2", {"query": "model context protocol"})
        print(result.structured_content, '\n')

        # 呼叫 MCP Server 的 resource
        # resources = group.resources       
        # for resource in resources.values():
            # print(f"名稱: {resource.name}\nURI: {resource.uri}\n說明: {resource.description}\n")
        
        # read resource from session_library2
        resource_content = await session_library2.read_resource("library://hours")
        content_block = resource_content.contents[0]
        if isinstance(content_block, TextResourceContents):
            print(f"Resource content: {content_block.text}")


    # 呼叫 MCP Server Group, 以 MCP Server 名稱區分工具函數
    async with ClientSessionGroup(component_name_hook=by_server) as group:
        await group.connect_to_server(library)
        await group.connect_to_server(web)

        # 呼叫 MCP Server 工具函數
        result = await group.call_tool("Web.search", {"query": "model context protocol"})
        print(result.structured_content)


# 測試  
if __name__ == "__main__":
    asyncio.run(main())