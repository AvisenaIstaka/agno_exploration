from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat, OpenAILike
from agno.os import AgentOS
from agno.tools.reasoning import ReasoningTools
from agno.tools.mcp import MCPTools
from dotenv import load_dotenv
from hooks.pre_hooks import validate_out_of_context
from knowledge import knowledge
from agno.models.huggingface import HuggingFace
from agno.db.postgres import PostgresDb
from sql_agent import sql_agent


load_dotenv()

db = PostgresDb(
    id="my_agent_db",
    db_url="postgresql://agno_user:admin@localhost:5432/agno_db"
)

local_agent = Agent(
    name="Local Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    add_history_to_context=True,
    enable_agentic_memory=True,
    db=db
)

general_agent = Agent(
    name="Houpe Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    add_history_to_context=True,
    instructions="""
    Kamu adalah customer support yang bekerja untuk bisnis Hipnoterapi Houpe. Gunakan gaya bahasa gen Z dan sapaan Kakak/kak kepada customer.
    Gunakan sudut pandang orang pertama untuk merujuk ke Houpe.
    Jawab pertanyaan hanya berdasarkan konteks.
    Jelaskan secara mendetail dan jelas dari konteks yang tersedia.
    Jika informasi tidak ditemukan, bilang dengan sopan bahwa kamu belum punya datanya.
    """,
    markdown=True,
    knowledge=knowledge,
    tools=[
        ReasoningTools(
            add_instructions=True,
            instructions="Gunakan tools untuk mendapatkan jawaban terkait Houpe"
        ),
    ],
)

dsi_agent = Agent(
    name="DSI Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    add_history_to_context=True,
    instructions="""
    Kamu adalah customer support yang bekerja untuk bisnis Duta Sarana Inovasi. Gunakan gaya bahasa gen Z dan sapaan Kakak/kak kepada customer.
    Gunakan sudut pandang orang pertama untuk merujuk ke Houpe.
    Jawab pertanyaan hanya berdasarkan konteks.
    Jelaskan secara mendetail dan jelas dari konteks yang tersedia.
    Jika informasi tidak ditemukan, bilang dengan sopan bahwa kamu belum punya datanya.
    """,
    markdown=True,
    knowledge=knowledge,
    knowledge_filters={"title":"dutasaranainovasi"},
    tools=[
        ReasoningTools(
            add_instructions=True,
            instructions="Gunakan tools untuk mendapatkan jawaban terkait Duta Sarana Inovasi"
        ),
    ],
)


leave_agent = Agent(
    name="Leave Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    db=SqliteDb(db_file="agno.db"),
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

agent_os = AgentOS(
    agents=[sql_agent, local_agent, general_agent, dsi_agent]
)

app = agent_os.get_app()

