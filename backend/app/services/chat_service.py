"""Chat service to answer user questions using retrieved RAG context."""

from sqlalchemy.ext.asyncio import AsyncSession
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.config import settings
from backend.app.models.chat import ChatMessage


async def answer_question(session_id: int, query: str, context: str, db: AsyncSession) -> str:
    """
    Answer a user's question using only the provided context, and save the chat history.

    Args:
        session_id: The ID of the research session.
        query: The user's question.
        context: The text chunks retrieved from the database.
        db: The SQLAlchemy async session.

    Returns:
        The AI's answer.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.2, 
        google_api_key=settings.google_api_key
    )
    
    parser = StrOutputParser()
    
    prompt = PromptTemplate(
        template=(
            "You are a helpful research assistant answering questions about a specific research topic.\n"
            "Answer the user's question using ONLY the provided context below. "
            "If the answer is not contained in the context, politely state that you don't have enough "
            "information from the research sources to answer it. Do NOT make up information.\n\n"
            "Context:\n"
            "{context}\n\n"
            "Question: {query}\n\n"
            "Answer:"
        ),
        input_variables=["context", "query"]
    )
    
    chain = prompt | llm | parser
    
    try:
        answer = await chain.ainvoke({
            "context": context,
            "query": query
        })
        answer = answer.strip()
    except Exception as e:
        print(f"Failed to generate chat answer: {e}")
        answer = "I'm sorry, I encountered an error while trying to answer your question."

    try:
        user_msg = ChatMessage(session_id=session_id, role="user", content=query)
        db.add(user_msg)
        
        ai_msg = ChatMessage(session_id=session_id, role="assistant", content=answer)
        db.add(ai_msg)
        
        await db.commit()
    except Exception as e:
        print(f"Failed to save chat history: {e}")
        await db.rollback()
        
    return answer
