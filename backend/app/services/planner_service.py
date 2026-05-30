"""Planner service for generating research questions."""

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.app.core.config import settings


class QuestionsOutput(BaseModel):
    """Output structure for the planner service."""
    
    questions: list[str] = Field(description="List of exactly 3 focused research questions")


async def generate_questions(topic: str) -> list[str]:
    """
    Generate focused research questions for a given topic.

    Args:
        topic: The research topic.

    Returns:
        A list of research questions.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.7,
        google_api_key=settings.google_api_key
    )
    
    parser = JsonOutputParser(pydantic_object=QuestionsOutput)
    
    prompt = PromptTemplate(
        template=(
            "You are an expert research planner.\n"
            "Generate exactly 3 focused research questions for the following topic: {topic}\n\n"
            "{format_instructions}"
        ),
        input_variables=["topic"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    
    response = await chain.ainvoke({"topic": topic})
    return response.get("questions", [])
