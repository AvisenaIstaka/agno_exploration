from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from app.config.settings import settings
from agno.tools.mcp import MCPTools

leave_agent = Agent(
    name="Leave Agent",
    model=OpenAIChat(
        id=settings.RUNPOD_MODEL_NAME,
        base_url=settings.RUNPOD_BASE_URL,
        api_key=settings.RUNPOD_API_KEY
    ),
    tools=[
        MCPTools(
            transport="streamable-http",
            url="http://localhost:3333/mcp"
        ),
        ReasoningTools(add_instructions=True),
    ],
    instructions="""
    You are an HR assistant.
    Use the GetLeaveAccrual tool to answer questions about leave balance.
    If the question is unrelated to HR or leave topics,
    politely decline and redirect the user.
    """,
    add_history_to_context=True,
    markdown=True,
    debug_mode=True,
)