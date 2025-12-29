from datetime import timedelta
from bson import ObjectId
from fastapi import HTTPException, status
from app.database import get_database
from app.models import AdminModel
from app.schemas import AdminCreate, AdminLogin, AdminResponse, TokenResponse
from app.utils import hash_password, verify_password, create_access_token
from app.config import settings


async def register_admin(admin_data: AdminCreate) -> AdminResponse:
    """Register a new admin user."""
    db = get_database()
    
    # Check if email already exists
    existing = await db.admins.find_one({"email": admin_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create admin document
    admin_doc = {
        "name": admin_data.name,
        "email": admin_data.email,
        "password_hash": hash_password(admin_data.password),
        "role": "admin"
    }
    
    result = await db.admins.insert_one(admin_doc)
    
    return AdminResponse(
        id=str(result.inserted_id),
        name=admin_data.name,
        email=admin_data.email,
        role="admin"
    )


async def authenticate_admin(login_data: AdminLogin) -> TokenResponse:
    """Authenticate admin and return JWT token."""
    db = get_database()
    
    # Find admin by email
    admin = await db.admins.find_one({"email": login_data.email})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, admin["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    token_data = {
        "sub": str(admin["_id"]),
        "email": admin["email"],
        "role": admin.get("role", "admin")
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    
    admin_response = AdminResponse(
        id=str(admin["_id"]),
        name=admin["name"],
        email=admin["email"],
        role=admin.get("role", "admin")
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        admin=admin_response
    )


async def get_admin_by_id(admin_id: str) -> AdminResponse:
    """Get admin by ID."""
    db = get_database()
    
    admin = await db.admins.find_one({"_id": ObjectId(admin_id)})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return AdminResponse(
        id=str(admin["_id"]),
        name=admin["name"],
        email=admin["email"],
        role=admin.get("role", "admin")
    )
