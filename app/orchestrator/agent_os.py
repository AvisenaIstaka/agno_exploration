from agno.os import AgentOS
from app.agents.sql_agent import sql_agent
from app.agents.business_agent import business_agent

agent_os = AgentOS(
    agents=[
        sql_agent,
        business_agent,
    ],
)
