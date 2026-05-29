"""Main FastAPI application entry point and routing setup."""

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.auth import router as auth_router
from backend.app.api.sessions import router as sessions_router
from backend.app.database.connection import get_db

app = FastAPI()
app.include_router(auth_router)
app.include_router(sessions_router)


@app.get("/health")
def health():
    """Basic application health check endpoint."""
    return {"status": "ok"}


@app.get("/db-health")
async def db_health(db: AsyncSession = Depends(get_db)):
    """Database connection health check endpoint."""
    await db.execute(text("SELECT 1"))
    return {"status": "database connected"}
