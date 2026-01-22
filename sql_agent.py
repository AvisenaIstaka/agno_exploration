from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.reasoning import ReasoningTools
from agno.tools.mcp import MCPTools
from dotenv import load_dotenv
from knowledge import knowledge
from agno.db.postgres import PostgresDb
from agno.tools.sql import SQLTools
from semantic_model import SEMANTIC_MODEL_STR
from tools.save_query import save_validated_query, set_knowledge
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os

load_dotenv()

api_key = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
COLLECTION_NAME = "sql-agent-knowledge"

db_dummy_data = PostgresDb(
    id="my_agent_db",
    db_url="postgresql://agno_user:admin@localhost:5432/dummy_data"
)

vector_db = Qdrant(
    collection=COLLECTION_NAME,
    url=qdrant_url,
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small",
        dimensions=1536  # Explicitly set
    ),
    api_key=api_key, # (optional)
)

# Create a knowledge base with Qdrant
knowledge = Knowledge(
    vector_db=vector_db,
    max_results=4
)

sql_agent_knowledge = Knowledge(
    name="SQL Agent Knowledge",
    vector_db=vector_db,
    max_results=5,
    contents_db=db_dummy_data,
)

set_knowledge(sql_agent_knowledge)


system_message = f"""\
You are a Text-to-SQL agent with access to a PostgreSQL HCM database.

WORKFLOW
--------
1. Search knowledge base before writing SQL
2. Execute query and validate results
3. Ask if user wants to save query to knowledge base

TABLES
------
- departments, job_positions, employees, salary_history, attendance, performance_reviews, training_history

DATA QUALITY NOTES
------------------
- employment_status: 'Active', 'Inactive', 'On Leave', 'Terminated'
- attendance.status: 'Present', 'Absent', 'Late', 'Half Day', 'Remote'
- Ratings: DECIMAL(3,2) BETWEEN 1 AND 5
- Latest salary: Use MAX(effective_date) subquery on salary_history
- employees.manager_id: self-referencing (can be NULL)

SQL RULES
---------
- Always search knowledge base first
- Always show the SQL query used
- Default LIMIT 50
- Never SELECT *
- Include ORDER BY for rankings
- Never run destructive queries
- Filter employment_status = 'Active' for current data

At the end, show the SQL you run.

<semantic_model>
{SEMANTIC_MODEL_STR}
</semantic_model>
"""

sql_agent = Agent(
    name="SQL Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    db=db_dummy_data,
    system_message=system_message,
    tools=[
        SQLTools(db_url="postgresql://agno_user:admin@localhost:5432/dummy_data"),
        ReasoningTools(add_instructions=True),
        save_validated_query,
    ],
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    search_knowledge=True,
    add_history_to_context=True,
    num_history_runs=5,
    read_chat_history=True,
    read_tool_call_history=True,
    markdown=True,
)
