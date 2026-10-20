# 引入套件
from mcp.server import MCPServer
import sys
# import requests
import httpx2

# 建立 MCP server 物件
mcp = MCPServer("Demo")

# 定義天氣預報工具函數
# not work, 出現錯誤訊息『requests module not found』
# @mcp.tool()
# def get_weather(latitude:float, longitude:float) -> str:
    # """天氣預報"""
    # url = "https://api.open-meteo.com/v1/forecast" + \
        # f"?latitude={latitude}&longitude={longitude}&current=temperature_2m" + \
        # ",wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    # sys.stderr.write(f'latitude:{latitude}, longitude:{longitude}')
    # response = requests.get(url)
    # data = response.json()
    # return str(data['current']['temperature_2m'])
    
@mcp.tool()
async def get_weather(latitude:float, longitude:float) -> str:
    """天氣預報"""
    sys.stderr.write(f'latitude:{latitude}, longitude:{longitude}')
    url = "https://api.open-meteo.com/v1/forecast" + \
        f"?latitude={latitude}&longitude={longitude}&current=temperature_2m" + \
        ",wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    
    USER_AGENT = "weather-app/1.0"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return str(data['current']['temperature_2m'])
        except Exception:
            return None

# 資源(resource)
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 提示(prompt)
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."
    

# 啟動 MCP Server  
if __name__ == "__main__":
    # print('Server is running...')
    # https://py.sdk.modelcontextprotocol.io/run/#streamable-http
    # mcp.run(transport='stdio')
    mcp.run(transport='streamable-http')
