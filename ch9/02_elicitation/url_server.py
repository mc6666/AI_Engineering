# 引入套件
from typing import Annotated
from pydantic import BaseModel
from mcp.server import MCPServer
from mcp.server.mcpserver import Context
import sys

# 建立 MCP server 物件
mcp = MCPServer("Bistro")

# 定義工具函數
@mcp.tool()
async def pay_deposit(booking_id: str, ctx: Context) -> str:
    """Take the deposit that confirms a booking."""
    result = await ctx.elicit_url(
        message="Pay a $20 deposit to confirm your booking?",
        url=f"https://pay.example.com/deposit/{booking_id}",
        elicitation_id=f"deposit-{booking_id}",
    )
    sys.stderr.write('*** ')
    sys.stderr.write(result.action)
    if result.action == "accept":
        return "Complete the payment in your browser."
    return "No deposit taken. The booking expires in one hour."

# 確認是否已付款
@mcp.tool()
async def confirm_deposit(booking_id: str, ctx: Context) -> str:
    """Record a payment reported by the payment provider."""
    await ctx.session.send_elicit_complete(f"deposit-{booking_id}")
    return f"Deposit received for booking {booking_id}."       

# 啟動 MCP Server  
if __name__ == "__main__":
    # print('Server is running...')
    # https://py.sdk.modelcontextprotocol.io/run/#streamable-http
    mcp.run(transport='streamable-http')
    