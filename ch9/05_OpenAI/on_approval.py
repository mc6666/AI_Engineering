# 引入套件
import asyncio
import json
from agents import (
    Agent,
    HostedMCPTool,
    MCPToolApprovalFunctionResult,
    MCPToolApprovalRequest,
    Runner,
    RunResult,
    RunResultStreaming,
)
from auto_mode import confirm_with_fallback

# 是否獲得同意
def prompt_approval(request: MCPToolApprovalRequest) -> MCPToolApprovalFunctionResult:
    params: object = request.data.arguments or {}
    approved = confirm_with_fallback(
        f"Approve running tool (mcp: {request.data.name}, params: {json.dumps(params)})? (y/n) ",
        default=True,
    )
    result: MCPToolApprovalFunctionResult = {"approve": approved}
    if not approved:
        result["reason"] = "User denied"
    return result


# 適時呼叫 Agent 內的 MCP Server
async def main(verbose: bool) -> None:
    question = "Which language is the repository openai/codex written in?"

    run_result = await Runner.run(agent, question)
    while run_result.interruptions:
        run_result = await Runner.run(agent, run_result.to_state())
    print(run_result.final_output)

    if verbose:
        for item in run_result.new_items:
            print(item)

# 建立 Agent 物件
agent = Agent(
    name="MCP Assistant",
    instructions=(
        "You must always use the MCP tools to answer questions. "
        "Use the DeepWiki hosted MCP server to answer questions and do not ask the user for "
        "additional configuration."
    ),
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "deepwiki",
                "server_url": "https://mcp.deepwiki.com/mcp",
                "allowed_tools": ["ask_question"],
                "require_approval": "always",
            },
            on_approval_request=prompt_approval,
        )
    ],
)

# 測試  
if __name__ == "__main__":
    asyncio.run(main(verbose=False))
