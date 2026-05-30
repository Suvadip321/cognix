"""Summarization service for compressing extracted web content."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.config import settings


async def summarize_source(extracted_text: str, topic: str) -> str:
    """
    Summarize the extracted text from a web page.

    Args:
        extracted_text: The cleaned text from a web page.
        topic: The research topic to focus the summary on.

    Returns:
        A 2-3 paragraph summary of the text.
    """
    if not extracted_text or not extracted_text.strip():
        return ""

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.3,
        google_api_key=settings.google_api_key
    )
    
    parser = StrOutputParser()
    
    prompt = PromptTemplate(
        template=(
            "You are an expert research assistant.\n"
            "Summarize the following text in 2-3 paragraphs, focusing specifically on information relevant to the topic: '{topic}'.\n\n"
            "Text to summarize:\n"
            "{extracted_text}\n\n"
            "Summary:"
        ),
        input_variables=["topic", "extracted_text"]
    )
    
    chain = prompt | llm | parser
    
    try:
        summary = await chain.ainvoke({
            "topic": topic,
            "extracted_text": extracted_text
        })
        return summary.strip()
    except Exception as e:
        print(f"Failed to summarize text: {e}")
        return ""
