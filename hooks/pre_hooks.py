from agno.exceptions import CheckTrigger
from agno.run.agent import RunInput
from pydantic import BaseModel
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import ChatPromptTemplate
from langchain_classic.output_parsers import PydanticOutputParser
from agno.exceptions import CheckTrigger, InputCheckError


class ContextValidationResult(BaseModel):
    """Structured output for context validation"""
    is_relevant: bool
    reason: str
    category: Literal["leave_related", "hr_related", "completely_irrelevant"]

def validate_out_of_context(run_input: RunInput) -> None:
    user_question = run_input.input_content
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = PydanticOutputParser(
        pydantic_object=ContextValidationResult
    )

    prompt = ChatPromptTemplate.from_template("""
    You are a strict classifier.

    The assistant ONLY supports HR and leave-related questions.

    User question:
    {question}

    {format_instructions}
    """).partial(
        format_instructions=parser.get_format_instructions()
    )

    chain = prompt | llm | parser
    result = chain.invoke({
    "question": user_question
})
    print("RESULT", result)

    if not result.is_relevant:
        raise InputCheckError(
            f"{result.reason}",
            check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
        )
