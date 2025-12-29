from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """Schema for creating a new candidate user."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    name: str
    email: str
    phone: str


class AdminCreate(BaseModel):
    """Schema for creating a new admin."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class AdminLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str


class AdminResponse(BaseModel):
    """Schema for admin response."""
    id: str
    name: str
    email: str
    role: str


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: AdminResponse
