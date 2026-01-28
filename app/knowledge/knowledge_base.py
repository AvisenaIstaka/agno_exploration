
from agno.knowledge.knowledge import Knowledge
from app.database.postgres_db import get_postgres_db_dummy_data
from app.memory.vector_db import get_vector_db

def get_knowledge():
    return(Knowledge(
        vector_db=get_vector_db(),
        max_results=4
    ))

def get_knowledge_sql_agent():
    return(Knowledge(
    name="SQL Agent Knowledge",
    vector_db=get_vector_db(),
    max_results=5,
    contents_db=get_postgres_db_dummy_data(),
))