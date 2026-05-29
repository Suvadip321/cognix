"""Pydantic schemas for research sessions, questions, and sources."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    """Payload for creating a new research session."""
    topic: str


class SessionResponse(BaseModel):
    """Data returned when fetching a research session."""
    id: int
    topic: str
    status: str
    current_step: str | None = None
    report_markdown: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionResponse(BaseModel):
    """Data returned when fetching research questions for a session."""
    id: int
    question: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceResponse(BaseModel):
    """Data returned when fetching research sources for a session."""
    id: int
    title: str
    source_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
