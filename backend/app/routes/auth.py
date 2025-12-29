from fastapi import APIRouter, Depends
from app.schemas import (
    AdminCreate,
    AdminLogin,
    AdminResponse,
    TokenResponse
)
from app.services import register_admin, authenticate_admin
from app.utils import get_current_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/admin/register", response_model=AdminResponse)
async def register_new_admin(admin_data: AdminCreate):
    """
    Register a new admin user.
    
    - **name**: Admin's full name
    - **email**: Admin's email address (must be unique)
    - **password**: Password (minimum 8 characters)
    """
    return await register_admin(admin_data)


@router.post("/admin/login", response_model=TokenResponse)
async def login_admin(login_data: AdminLogin):
    """
    Authenticate admin and get JWT token.
    
    - **email**: Admin's email address
    - **password**: Admin's password
    
    Returns a JWT token for authenticated requests.
    """
    return await authenticate_admin(login_data)


@router.get("/admin/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """Get current admin info from JWT token."""
    from app.services import get_admin_by_id
    return await get_admin_by_id(str(current_admin["_id"]))
