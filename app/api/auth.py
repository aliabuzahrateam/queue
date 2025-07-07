from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.services.auth import auth_service, get_current_user, get_current_super_admin
from app.services.database import get_db
from app.models.application import Application
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str
    role: str
    app_id: Optional[str] = None

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    # For demo purposes, we'll use a simple admin check
    # In production, you'd have a proper user table
    admin_email = "admin@yourcompany.com"  # This should come from env
    admin_password = "changeme123"  # This should come from env
    
    if form_data.username == admin_email and form_data.password == admin_password:
        # Create access token
        access_token = auth_service.create_access_token(
            data={
                "sub": admin_email,
                "role": "super_admin",
                "email": admin_email
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    # Check if it's an application API key
    app = db.query(Application).filter_by(
        api_key=form_data.password,
        is_active=True,
        is_deleted=False
    ).first()
    
    if app and form_data.username == app.name:
        access_token = auth_service.create_access_token(
            data={
                "sub": app.name,
                "role": "app_admin",
                "app_id": str(app.id),
                "email": f"{app.name}@app.local"
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        email=current_user.get("email"),
        role=current_user.get("role"),
        app_id=current_user.get("app_id")
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    # Create new token with extended expiry
    access_token = auth_service.create_access_token(
        data={
            "sub": current_user.get("sub"),
            "role": current_user.get("role"),
            "app_id": current_user.get("app_id"),
            "email": current_user.get("email")
        },
        expires_delta=timedelta(minutes=60)  # Extended expiry
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/health")
async def auth_health():
    """Health check for authentication service"""
    return {"status": "healthy", "service": "authentication"} 