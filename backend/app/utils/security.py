"""
Security utilities for authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import get_database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/admin/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_admin(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current authenticated admin."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    
    from bson import ObjectId
    db = get_database()
    admin = await db.admins.find_one({"_id": ObjectId(admin_id)})
    if admin is None:
        raise credentials_exception
    
    return admin


def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID for test links and sessions."""
    import uuid
    return f"{prefix}{str(uuid.uuid4())}"
