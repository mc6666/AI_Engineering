# 引入套件
from dataclasses import dataclass
from agents import Agent, GenerateDynamicPromptData, Runner
from dotenv import load_dotenv
import os
import asyncio

# 讀取組態檔
load_dotenv('../.env')
MODEL_ID = os.getenv('MODEL_ID')

# prompt 資訊
@dataclass
class PromptContext:
    prompt_id: str
    poem_style: str

# 定義動態呼叫提示模板的函數
async def build_prompt(data: GenerateDynamicPromptData):
    ctx: PromptContext = data.context.context
    return {
        "id": ctx.prompt_id,
        "version": "1",
        "variables": {"poem_style": ctx.poem_style},
    }

# 建立 Agent 物件
agent = Agent(name="Prompted assistant", prompt=build_prompt, model=MODEL_ID)

# 呼叫API
async def main():
    prompt = "Say hello"
    result = await Runner.run(
        agent,
        prompt,
        context=PromptContext(prompt_id="pmpt_6a9ac2ff6f848193a5ab92d3aacd415304eeeff5e8a6d7ee"
            , poem_style="limerick"),
    )

    # 顯示回應
    print(result.final_output)

# 測試
if __name__ == "__main__":
    asyncio.run(main())    