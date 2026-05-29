"""Pydantic schemas for authentication and user data validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SignupRequest(BaseModel):
    """Schema for user registration requests."""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Schema for user login requests."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token responses."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for representing user data in responses."""
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
