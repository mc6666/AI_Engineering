# 引入套件
from mcp.server import MCPServer
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse

# 建立 MCP server 物件
mcp = MCPServer("Notes")

# 定義工具函數
@mcp.tool()
def add_note(text: str) -> str:
    """Save a note."""
    return f"Saved: {text}"

# 定義一般函數
async def homepage(request):
    return JSONResponse({'hello': 'world'})

# 定義 Context Manager
@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
        yield


# 掛載 MCP server 至 Starlette 網頁伺服器
app = Starlette(
    routes=[
        Route('/', homepage),
        Mount("/", app=mcp.streamable_http_app()),
        ],
    lifespan=lifespan,
)

