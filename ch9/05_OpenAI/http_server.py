# 引入套件
from mcp.server import MCPServer
import asyncio
import sys
import httpx2

# 建立 MCP server 物件
mcp = MCPServer("Weather")

# 工具函數
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


# 啟動 MCP Server  
if __name__ == "__main__":
    mcp.run(transport='streamable-http')
