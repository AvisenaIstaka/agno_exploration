from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from app.services.semantic_model import SEMANTIC_MODEL_STR
from app.knowledge.knowledge_base import get_knowledge_sql_agent
from app.config.settings import settings
from app.tools.save_query import save_validated_query, set_knowledge
from app.database.postgres_db import get_postgres_db_dummy_data
from agno.tools.sql import SQLTools
from app.config.settings import settings

set_knowledge(get_knowledge_sql_agent)

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

<semantic_model>
{SEMANTIC_MODEL_STR}
</semantic_model>
"""

sql_agent = Agent(
    name="SQL Agent",
    model=OpenAIChat(
        id=settings.RUNPOD_MODEL_NAME,
        base_url=settings.RUNPOD_BASE_URL,
        api_key=settings.RUNPOD_API_KEY
    ),
    db=get_postgres_db_dummy_data(),
    system_message=system_message,
    tools=[
        SQLTools(db_url=settings.POSTGRES_URL_DUMMY_DATA),
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
    compress_tool_results=True,
)


# run_response = sql_agent.run("siapa?")

# for requirement in run_response.active_requirements:
#     te = requirement.tool_execution

#     if te and te.requires_confirmation:
#         print(
#             f"Tool {te.tool_name}({te.tool_args}) requires confirmation"
#         )

#         confirmed = input("Confirm? (y/n): ").lower() == "y"

#         # Set confirmation flag
#         te.confirmed = confirmed

# # After resolving the requirement, you can continue the run:
# response = sql_agent.continue_run(run_id=run_response.run_id, requirements=run_response.requirements)
# print(response.content)
