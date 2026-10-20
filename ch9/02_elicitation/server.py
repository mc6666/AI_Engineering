# 引入套件
from typing import Annotated
from pydantic import BaseModel
from mcp.server import MCPServer
from mcp.server.mcpserver import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
    Elicit,
    ElicitationResult,
    Resolve,
)

# 建立 MCP server 物件
mcp = MCPServer("Files")

# 允許操作的資料夾及檔案
_FOLDERS: dict[str, list[str]] = {"./tmp/empty": [], "./tmp/project": ["main.py", "README.md"]}

# 誘導(Elicitation)的資訊
class Confirm(BaseModel):
    ok: bool

# 依據 MCP Client 收集的表單決定是否刪除目錄或檔案
async def confirm_delete(path: str) -> Confirm | Elicit[Confirm]:
    """資料夾內有檔案，刪除前會先確認"""
    file_count = len(_FOLDERS.get(path, []))
    if file_count == 0:
        return Confirm(ok=True)  # nothing to confirm, no round-trip to the client
    return Elicit(f"{path} has {file_count} file(s). Delete anyway?", Confirm)


# 定義工具函數
@mcp.tool()
async def delete_folder(
    path: str,
    confirm: Annotated[ElicitationResult[Confirm], Resolve(confirm_delete)],
) -> str:
    """刪除或保留資料夾的模擬"""
    match confirm:
        case AcceptedElicitation(data=Confirm(ok=True)):
            _FOLDERS.pop(path, None)
            return f"deleted {path}"
        case AcceptedElicitation(): # Client 傳送y以外
            return "kept the folder"
        case DeclinedElicitation():
            return "declined: folder not deleted"
        case CancelledElicitation():
            return "cancelled: folder not deleted"

# 啟動 MCP Server  
if __name__ == "__main__":
    # print('Server is running...')
    # https://py.sdk.modelcontextprotocol.io/run/#streamable-http
    mcp.run(transport='streamable-http')
            