"""Evaluator service for scoring and filtering search results."""

import asyncio
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.app.core.config import settings


class SourceScore(BaseModel):
    """Output structure for scoring a single source."""
    
    relevance: int = Field(description="Relevance to the topic (1-5)")
    credibility: int = Field(description="Credibility of the source based on URL and title (1-5)")
    usefulness: int = Field(description="Usefulness of the snippet facts (1-5)")


async def evaluate_sources(sources: list[dict], topic: str, top_k: int = 5) -> list[dict]:
    """
    Evaluate and score a list of sources using an LLM.

    Args:
        sources: List of dictionaries containing title, url, and snippet.
        topic: The overarching research topic.
        top_k: The number of top sources to return.

    Returns:
        List of the top sources sorted by their total score, limited by top_k.
    """
    if not sources:
        return []

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.0, 
        google_api_key=settings.google_api_key
    )
    
    parser = JsonOutputParser(pydantic_object=SourceScore)
    
    prompt = PromptTemplate(
        template=(
            "You are an expert researcher. Evaluate the following source for its value in writing a report on the topic: '{topic}'.\n\n"
            "Source Title: {title}\n"
            "Source URL: {url}\n"
            "Source Snippet: {snippet}\n\n"
            "Score the source on a scale of 1 to 5 for:\n"
            "1. Relevance: Does the snippet directly address the topic?\n"
            "2. Credibility: Is the source likely to be reliable (based on URL/title)?\n"
            "3. Usefulness: Does the snippet contain concrete facts, data, or arguments?\n\n"
            "{format_instructions}"
        ),
        input_variables=["topic", "title", "url", "snippet"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser

    async def _evaluate_single(source: dict) -> dict:
        try:
            score_data = await chain.ainvoke({
                "topic": topic,
                "title": source.get("title", "Unknown"),
                "url": source.get("url", "Unknown"),
                "snippet": source.get("snippet", "")
            })
            
            relevance = score_data.get("relevance", 0)
            credibility = score_data.get("credibility", 0)
            usefulness = score_data.get("usefulness", 0)
            total_score = relevance + credibility + usefulness

            evaluated_source = source.copy()
            evaluated_source["relevance_score"] = relevance
            evaluated_source["credibility_score"] = credibility
            evaluated_source["usefulness_score"] = usefulness
            evaluated_source["total_score"] = total_score
            return evaluated_source
            
        except Exception as e:
            print(f"Evaluation failed for {source.get('url')}: {e}")
            evaluated_source = source.copy()
            evaluated_source["relevance_score"] = 0
            evaluated_source["credibility_score"] = 0
            evaluated_source["usefulness_score"] = 0
            evaluated_source["total_score"] = 0
            return evaluated_source

    tasks = [_evaluate_single(s) for s in sources]
    evaluated_sources = await asyncio.gather(*tasks)
    evaluated_sources.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    
    return evaluated_sources[:top_k]
