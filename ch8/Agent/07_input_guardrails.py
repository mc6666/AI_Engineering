# 引入套件
import asyncio, os
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

# 護欄輸出欄位
class MRT_Output(BaseModel):
    is_MRT_related: bool
    reasoning: str

# 護欄Agent
guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="判定問題是否與台北捷運有關.",
    output_type=MRT_Output,
)


# 護欄輸入檢查
@input_guardrail
async def mrt_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered= not result.final_output.is_MRT_related,
    )


# 一般 Agent
agent = Agent(  
    name="Customer support agent",
    instructions="你是客服人員，負責回答客戶問題.",
    input_guardrails=[mrt_guardrail],
)

# 主程式
async def main():
    # 只處理台北捷運相關問題
    while True:
        prompt = input('輸入提示:\n')
        if len(prompt) == 0: break
        try:
            result = await Runner.run(agent, prompt)
            print("通過台北捷運護欄")
            print('回應：', result.final_output)  
        except InputGuardrailTripwireTriggered:
            print("遭台北捷運護欄阻擋")

# 測試
if __name__ == "__main__":
    asyncio.run(main())        
        