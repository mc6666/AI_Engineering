# 引入套件
import asyncio
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace
from auto_mode import input_with_fallback

# Sub-agents
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You translate the user's message to Spanish",
    handoff_description="An english to spanish translator",
)

french_agent = Agent(
    name="french_agent",
    instructions="You translate the user's message to French",
    handoff_description="An english to french translator",
)

chinese_agent = Agent(
    name="chinese_agent",
    instructions="You translate the user's message to Traditional Chinese",
    handoff_description="An english to chinese translator",
)

# orchestrator agent
orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools in order."
        "You never translate on your own, you always use the provided tools."
    ),
    tools=[
        # agent as tool
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
        chinese_agent.as_tool(
            tool_name="translate_to_chinese",
            tool_description="Translate the user's message to Chinese",
        ),
    ],
)

# synthesizer agent
synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions="You inspect translations, correct them if needed, and produce a final concatenated response.",
)


# 呼叫 Agent
async def main():
    msg = input_with_fallback(
        "Hi! What would you like translated, and to which languages? ",
        "Translate 'Hello, world!' to French and Spanish.", # fallback
    )

    # Run the entire orchestration in a single trace
    with trace("Orchestrator evaluator"):
        orchestrator_result = await Runner.run(orchestrator_agent, msg)
        
        # print("orchestrator_result:")
        # print(orchestrator_result)
        for item in orchestrator_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"  - Translation step:\n{text}")

        synthesizer_result = await Runner.run(
            synthesizer_agent, orchestrator_result.to_input_list()
        )

    print(f"\n\nFinal response:\n{synthesizer_result.final_output}")


# 測試
if __name__ == "__main__":
    asyncio.run(main())
