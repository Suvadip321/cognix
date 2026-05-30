"""Retrieval service for semantic search using pgvector."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.app.core.config import settings
from backend.app.models.chat import DocumentChunk


async def retrieve_chunks(session_id: int, query: str, db: AsyncSession, limit: int = 5) -> str:
    """
    Search the document_chunks table for the most relevant text chunks using vector similarity.

    Args:
        session_id: The ID of the current research session.
        query: The user's chat question.
        db: The SQLAlchemy async session.
        limit: Max number of chunks to return.

    Returns:
        A formatted string containing the top relevant text chunks.
    """
    if not query:
        return ""

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.google_api_key
    )
    
    try:
        query_vector = await embeddings_model.aembed_query(query)
    except Exception as e:
        print(f"Failed to embed query: {e}")
        return ""

    try:
        stmt = (
            select(DocumentChunk)
            .filter(DocumentChunk.session_id == session_id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        top_chunks = result.scalars().all()
        
        if not top_chunks:
            return "No relevant context found in the research documents."
            
        context = "\n\n---\n\n".join(
            f"[Source chunk {i+1}]:\n{chunk.content}" 
            for i, chunk in enumerate(top_chunks)
        )
        
        return context
        
    except Exception as e:
        print(f"Failed to retrieve chunks from database: {e}")
        return ""
