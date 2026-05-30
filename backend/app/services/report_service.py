"""Report service for generating the final comprehensive markdown research report."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.config import settings


async def generate_report(topic: str, summaries: list[str]) -> str:
    """
    Generate a comprehensive markdown report using all the gathered summaries.

    Args:
        topic: The original research topic.
        summaries: A list of all summaries gathered from the search process.

    Returns:
        A fully formatted markdown report string.
    """
    if not summaries:
        return f"# Research Report: {topic}\n\nNo sufficient information could be found on this topic."

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.4, # Slightly higher temperature for better narrative flow and readability
        google_api_key=settings.google_api_key
    )
    
    parser = StrOutputParser()
    
    combined_summaries = "\n\n---\n\n".join(f"Source {i+1}:\n{summary}" for i, summary in enumerate(summaries))
    
    prompt = PromptTemplate(
        template=(
            "You are an expert medical researcher and technical writer.\n"
            "Your task is to synthesize the provided research summaries into a highly professional, "
            "comprehensive, and well-structured markdown report on the topic: '{topic}'.\n\n"
            "Requirements:\n"
            "- Use proper markdown formatting (H1 for title, H2/H3 for sections, bullet points, bold text for emphasis).\n"
            "- Create a logical flow: Introduction, Main Findings/Themes, Challenges/Limitations, and Conclusion.\n"
            "- Synthesize the information intelligently. Do not just list the summaries one by one.\n"
            "- Maintain an objective, academic, and authoritative tone.\n\n"
            "Research Summaries:\n"
            "{combined_summaries}\n\n"
            "Write the final markdown report below:"
        ),
        input_variables=["topic", "combined_summaries"]
    )
    
    chain = prompt | llm | parser
    
    try:
        report = await chain.ainvoke({
            "topic": topic,
            "combined_summaries": combined_summaries
        })
        return report.strip()
    except Exception as e:
        print(f"Failed to generate report: {e}")
        return f"# Error generating report\n\nAn error occurred while compiling the research data: {str(e)}"
