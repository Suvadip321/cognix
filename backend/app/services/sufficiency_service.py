"""Sufficiency service for checking if enough information has been gathered."""

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.app.core.config import settings


class SufficiencyOutput(BaseModel):
    """Output structure for the sufficiency check."""
    
    enough: bool = Field(description="True if the summaries provide enough information to write a comprehensive report on the topic, False otherwise")
    missing_areas: list[str] = Field(description="If enough is False, list up to 3 specific areas or sub-topics that are missing and need more research. If enough is True, this should be an empty list.")


async def check_sufficiency(topic: str, summaries: list[str]) -> dict:
    """
    Check if the collected summaries contain enough information to write a full report.

    Args:
        topic: The overarching research topic.
        summaries: A list of summarized texts from various sources.

    Returns:
        A dictionary containing 'enough' (bool) and 'missing_areas' (list of strings).
    """
    if not summaries:
        return {"enough": False, "missing_areas": ["All core aspects of the topic"]}

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.0, 
        google_api_key=settings.google_api_key
    )
    
    parser = JsonOutputParser(pydantic_object=SufficiencyOutput)
    
    combined_summaries = "\n\n---\n\n".join(f"Summary {i+1}:\n{summary}" for i, summary in enumerate(summaries))
    
    prompt = PromptTemplate(
        template=(
            "You are an expert research editor.\n"
            "Your task is to review the provided research summaries and determine if there is enough "
            "comprehensive information to write a high-quality, full markdown research report on the topic: '{topic}'.\n\n"
            "Collected Summaries:\n"
            "{combined_summaries}\n\n"
            "Does this provide enough information? If not, what specific areas are missing?\n\n"
            "{format_instructions}"
        ),
        input_variables=["topic", "combined_summaries"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        result = await chain.ainvoke({
            "topic": topic,
            "combined_summaries": combined_summaries
        })
        return {
            "enough": result.get("enough", False),
            "missing_areas": result.get("missing_areas", [])
        }
    except Exception as e:
        print(f"Sufficiency check failed: {e}")
        return {"enough": True, "missing_areas": []}
