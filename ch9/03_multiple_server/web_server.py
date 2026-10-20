# 引入套件
from mcp.server import MCPServer

# 建立 MCP server 物件
mcp = MCPServer("Web")

# 定義工具函數
@mcp.tool()
def search(query: str) -> str:
    """Search the web."""
    return f"12 pages match {query!r}."