# 引入套件
from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier
from fastmcp.server.auth.providers.jwt import RSAKeyPair
import random
import logging

# 產生金鑰
key_pair = RSAKeyPair.generate()
access_token = key_pair.create_token(audience="dice-server")

# 將 Access token 寫入檔案
with open('access_token.txt', 'w', encoding = 'utf8') as f:
    f.write(access_token)

# 指定 JWT 權限控管機制
auth = JWTVerifier(
    public_key=key_pair.public_key, # 公鑰
    audience="dice-server",
)

# 設定 Log 組態
logging.basicConfig(filename='auth_server.log', level=logging.INFO)

# 建立 MCP server 物件
mcp = FastMCP(name="Dice Roller", auth=auth)

# 定義工具函數
@mcp.tool
def roll_dice(n_dice: int) -> list[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

# 啟動 MCP server
if __name__ == "__main__":
    mcp.run(transport='http', port=8000, log_level="DEBUG")