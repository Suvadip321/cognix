"""Embedding service to vectorise research chunks."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.models.chat import DocumentChunk


async def embed_and_store(session_id: int, source_id: int, text: str, db: AsyncSession):
    """
    Split the extracted text into chunks, generate embeddings for each,
    and store them in the database for later RAG retrieval.
    
    Args:
        session_id: The ID of the research session.
        source_id: The ID of the research source this text belongs to.
        text: The raw, full-length extracted text from the web page.
        db: The SQLAlchemy async session.
    """
    if not text or not text.strip():
        return
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_text(text)
    
    if not chunks:
        return

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.google_api_key
    )
    
    try:
        vectors = await embeddings_model.aembed_documents(chunks)
        
        for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
            doc_chunk = DocumentChunk(
                session_id=session_id,
                source_id=source_id,
                chunk_index=i,
                content=chunk_text,
                embedding=vector
            )
            db.add(doc_chunk)
            
        await db.commit()
    except Exception as e:
        print(f"Failed to embed and store chunks: {e}")
        await db.rollback()
