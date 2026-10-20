# 引入套件
import asyncio
from agents import Agent, HostedMCPTool, ModelSettings, Runner, RunResult

# 建立 Agent 物件
agent = Agent(
    name="Assistant",
    model_settings=ModelSettings(tool_choice="required"),
    tools=[
        # OpenAI 內建的 MCP Server -- DeepWiki
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "deepwiki",
                "server_url": "https://mcp.deepwiki.com/mcp",
                "require_approval": "never",
            }
        )
    ],
)

# 適時呼叫 Agent 內的 MCP Server
async def main(repo: str):
    question = f"Which language is the repository {repo} written in?"
    agent.instructions=f"You can use the DeepWiki hosted MCP server to inspect {repo}."
    run_result = await Runner.run(agent, question)
    print(f'repo:{repo} -- {run_result.final_output}')
    # print('\n更詳細的回應資訊：')
    # for item in run_result.new_items:
        # print(item)

# 測試  
if __name__ == "__main__":
    asyncio.run(main('https://github.com/kootenpv/yagmail'))
    asyncio.run(main('https://github.com/RestoreMonarchy/Servers'))
