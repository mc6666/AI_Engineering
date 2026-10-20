# 引入套件
from mcp.server import MCPServer
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI

# 建立 MCP server 物件
mcp = MCPServer("Notes")

# 定義 Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
        yield

# 建立 FastAPI 物件
app = FastAPI(lifespan=lifespan)

# 定義工具函數
@mcp.tool()
def add_note(text: str) -> str:
    """Save a note."""
    return f"Saved: {text}"

# 定義一般函數
@app.get("/")
async def homepage():
    return 'hello world'

# 掛載 MCP server 至 FastAPI 網頁伺服器
app.mount("/", app=mcp.streamable_http_app())