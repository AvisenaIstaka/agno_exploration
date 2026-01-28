from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from app.knowledge.knowledge_base import get_knowledge
from app.config.settings import settings
from app.database.postgres_db import get_postgres_db
from app.config.settings import settings
from agno.learn import LearningMachine, LearningMode, UserMemoryConfig

business_agent = Agent(
    name="Business Agent",
    id="houpe-agentic",
    db=get_postgres_db(),
    learning=LearningMachine(
        user_memory=UserMemoryConfig(
            mode=LearningMode.ALWAYS,
        ),
    ),
    enable_agentic_memory=True,
    model=OpenAIChat(
        id=settings.RUNPOD_MODEL_NAME,
        base_url=settings.RUNPOD_BASE_URL,
        api_key=settings.RUNPOD_API_KEY
    ),
    add_history_to_context=True,
    add_knowledge_to_context=True,
    instructions="""
    Kamu adalah customer support yang bekerja untuk bisnis Hipnoterapi Houpe. Gunakan gaya bahasa gen Z dan sapaan Kakak/kak kepada customer.
    Gunakan sudut pandang orang pertama untuk merujuk ke Houpe.
    Jawab pertanyaan hanya berdasarkan konteks.
    Jelaskan secara mendetail dan jelas dari konteks yang tersedia.
    Jika informasi tidak ditemukan, bilang dengan sopan bahwa kamu belum punya datanya.
    """,
    markdown=True,
    knowledge=get_knowledge(),
    knowledge_filters={
        "meta_data.title": "houpe_info",
    },
    tools=[
        ReasoningTools(
            add_instructions=True,
            instructions="Gunakan tools untuk mendapatkan jawaban terkait Houpe"
        ),
    ],
)