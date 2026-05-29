"""Session API routes for creating, listing, and managing research sessions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user
from backend.app.database.connection import get_db
from backend.app.models.session import ResearchQuestion, ResearchSession, ResearchSource
from backend.app.models.user import User
from backend.app.schemas.session import (
    QuestionResponse,
    SessionCreate,
    SessionResponse,
    SourceResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResearchSession:
    """Create a new research session for the logged-in user."""
    session = ResearchSession(
        user_id=current_user.id,
        topic=payload.topic,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ResearchSession]:
    """List all research sessions belonging to the logged-in user."""
    result = await db.execute(
        select(ResearchSession)
        .where(ResearchSession.user_id == current_user.id)
        .order_by(ResearchSession.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResearchSession:
    """Get a specific research session. Ensures the user owns it."""
    result = await db.execute(
        select(ResearchSession).where(
            ResearchSession.id == session_id,
            ResearchSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or you don't have access",
        )

    return session


async def _verify_session_access(session_id: int, user_id: int, db: AsyncSession) -> None:
    """Helper to verify a session exists and belongs to the user."""
    result = await db.execute(
        select(ResearchSession.id).where(
            ResearchSession.id == session_id,
            ResearchSession.user_id == user_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or you don't have access",
        )


@router.get("/{session_id}/questions", response_model=list[QuestionResponse])
async def get_session_questions(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ResearchQuestion]:
    """Get all research questions generated for a specific session."""
    await _verify_session_access(session_id, current_user.id, db)
    
    result = await db.execute(
        select(ResearchQuestion)
        .where(ResearchQuestion.session_id == session_id)
        .order_by(ResearchQuestion.created_at.asc())
    )
    return result.scalars().all()


@router.get("/{session_id}/sources", response_model=list[SourceResponse])
async def get_session_sources(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ResearchSource]:
    """Get all web sources found and evaluated for a specific session."""
    await _verify_session_access(session_id, current_user.id, db)
    
    result = await db.execute(
        select(ResearchSource)
        .where(ResearchSource.session_id == session_id)
        .order_by(ResearchSource.created_at.asc())
    )
    return result.scalars().all()
