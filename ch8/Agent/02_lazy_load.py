# 引入套件
from agents import Agent, Runner, ToolSearchTool, tool_namespace
from agents.decorators import tool
import os, json, requests
from dotenv import load_dotenv
import asyncio

# 讀取組態檔
load_dotenv('../.env')
MODEL_ID = os.getenv('MODEL_ID')

## 定義天氣預報函數(get_weather)
@tool(defer_loading=True)
def get_weather(latitude:str, longitude:str):
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast" + \
        f"?latitude={latitude}&longitude={longitude}&current=temperature_2m" + \
        ",wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data['current']['temperature_2m']

# 建立 Agent 物件
tools = tool_namespace(
    name="weather_forecasting",
    description="weather forecasting.",
    tools=[get_weather],
)
agent = Agent(
    name="My agent",
    model=MODEL_ID,
    instructions="Load the namespace before using the tools.",
    tools=[*tools, ToolSearchTool()],
)

# 呼叫API
async def main():
    result = await Runner.run(
        agent,
        "今天台北天氣如何?",
    )

    # 顯示執行結果
    print(result.final_output)
    
if __name__ == "__main__":
    asyncio.run(main())    