# 引入套件
from __future__ import annotations
import json
import random
import asyncio
from agents import (
    Agent,
    HandoffInputData,
    Runner,
    handoff,
    trace,
)
from agents.decorators import tool

# 交接篩選器
def chinese_handoff_message_filter(handoff_message_data: HandoffInputData) -> HandoffInputData:
    return HandoffInputData(
        input_history=handoff_message_data.input_history,
        pre_handoff_items=tuple(handoff_message_data.pre_handoff_items),
        new_items=tuple(handoff_message_data.new_items),
    )

# Tool 函數
@tool
def random_number_tool(max: int) -> int:
    """Return a random integer between 0 and the given maximum."""
    return random.randint(0, max)

# Agents
first_agent = Agent(
    name="Assistant",
    instructions="Be extremely concise.",
    tools=[random_number_tool],
)

chinese_agent = Agent(
    name="Chinese Assistant",
    instructions="You only speak Traditional Chinese and are extremely concise.",
    handoff_description="A Chinese-speaking assistant.",
)

second_agent = Agent(
    name="Assistant",
    instructions=(
    "Be a helpful assistant. " +
    "If the user speaks Traditional Chinese, handoff to the Chinese assistant."
    ),
    handoffs=[handoff(chinese_agent, input_filter=chinese_handoff_message_filter)],
)

# 呼叫 Agent
async def main():
    # Trace the entire run as a single workflow
    with trace(workflow_name="Message filtering"):
        # 1. Send a regular message to the first agent
        result = await Runner.run(first_agent, input="Hi, my name is Sora.")
        print("Step 1 done")

        # 2. Ask it to generate a number
        result = await Runner.run(first_agent, input=result.to_input_list()
            + [{"content": 
            "Can you generate a random number between 0 and 100?", "role": "user"}],
        )
        print("Step 2 done")

        # 3. Call the second agent
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                "content": "I live in New York City. What's the population of the city?",
                "role": "user",
                }
            ],
        )
        print("Step 3 done")

        # 4. Cause a handoff to occur
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                "content": "我住哪裡？",
                "role": "user",
                }
            ],
        )
        print("Step 4 done")

    print("\n===Final messages===\n")

    # 5. That should have caused chinese_handoff_message_filter to be called, which means the
    # output should be missing the first two messages, and have no tool calls.
    # Let's print the messages to see what happened
    for message in result.to_input_list():
        print(json.dumps(message, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
