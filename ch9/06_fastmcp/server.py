# 引入套件
from fastmcp import FastMCP

# 建立 MCP server 物件
mcp = FastMCP("Demo")

# 定義工具函數
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# 啟動 MCP server
if __name__ == "__main__":
    mcp.run(transport='streamable-http')