from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class UserModel(BaseModel):
    """Candidate user model."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AdminModel(BaseModel):
    """Admin user model."""
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    password_hash: str
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="admin")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserInDB(UserModel):
    """User as stored in database."""
    pass


class AdminInDB(AdminModel):
    """Admin as stored in database."""
    pass
