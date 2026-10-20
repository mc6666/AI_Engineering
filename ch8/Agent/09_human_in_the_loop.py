# 引入套件
import asyncio
import json
from pathlib import Path

from agents import (
    Agent,
    Runner,
    RunState,
)
from agents.decorators import tool
from auto_mode import confirm_with_fallback


# 定義一般的Tool函數
@tool
async def print_order_information(amount: int) -> str:
    return f"The order amount: {amount}"


# 定義函數判斷請購單是否需經審核
async def need_human_approval(_ctx, params, _call_id) -> bool:
    return params.get("amount") >= 10_000

# 定義Tool函數需經審核
@tool(
    needs_approval=need_human_approval
)
async def high_amount_order(amount: int) -> str:
    return f"The request is approved"


# Agent
agent = Agent(
    name="Purchase Request Auditor",
    instructions=(
        "You are a helpful Purchase Request Processing assistant. " 
        "Answer questions about the Purchase Request using the available tools."
    ),
    tools=[print_order_information, high_amount_order],
)

# Log
RESULT_PATH = Path("human_in_the_loop/result.json")

# 審核
async def confirm(question: str) -> bool:
    return confirm_with_fallback(f"{question} (y/n): ", default=True)

# 主程式
async def main():
    """Run the human-in-the-loop example."""
    while True:
        prompt = input('輸入提示:\n') # Apply $20000 Purchase Request
        if len(prompt) == 0: break
        result = await Runner.run(
            agent,
            prompt,
        )

        has_interruptions = len(result.interruptions) > 0

        while has_interruptions:
            print("\n" + "=" * 80)
            print("Run interrupted - tool approval required")
            print("=" * 80)

            # 序列化(serialization)：將流程狀態寫入 "human_in_the_loop/result.json"
            state = result.to_state()
            state_json = state.to_json()
            RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with RESULT_PATH.open("w") as f:
                json.dump(state_json, f, indent=2)

            print(f"State saved to {RESULT_PATH}")

            # 反序列化(deserialization)：讀取 JSON 檔案，還原流程狀態
            print(f"Loading state from {RESULT_PATH}")
            with RESULT_PATH.open() as f:
                stored_state_json = json.load(f)

            state = await RunState.from_json(agent, stored_state_json)

            # 處理中斷
            for interruption in result.interruptions:
                print("\nTool call details:")
                print(f"  Agent: {interruption.agent.name}")
                print(f"  Tool: {interruption.name}")
                print(f"  Arguments: {interruption.arguments}")

                confirmed = await confirm("\nDo you approve this tool call?")

                if confirmed:
                    print(f"✓ Approved: {interruption.name}")
                    state.approve(interruption)
                else:
                    print(f"✗ Rejected: {interruption.name}")
                    state.reject(interruption)

            # 還原流程狀態，繼續後續流程
            print("\nResuming agent execution...")
            result = await Runner.run(agent, state)
            has_interruptions = len(result.interruptions) > 0

        # 顯示處理結果
        print("\n" + "=" * 80)
        print("Final Output:")
        print("=" * 80)
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
