# 引入套件
from mcp.server import MCPServer

# 建立 MCP server 物件
mcp = MCPServer("Library")

# 定義工具函數
@mcp.tool()
def search2(query: str) -> str:
    """Search the library catalog."""
    return f"3 books match {query!r}."

# 定義資源
@mcp.resource("library://hours")
def hours() -> str:
    """When the library is open."""
    return "Mon-Fri 09:00-17:00"