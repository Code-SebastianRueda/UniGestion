"""
Authentication routes.
Handles login, register, logout, and session management.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..models import User, CandidateProfile
from ..auth import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user as candidate."""
    # Check if email exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role="candidate"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create candidate profile
    profile = CandidateProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    # Generate token
    token = create_access_token({"sub": str(user.id), "role": user.role, "name": user.full_name})

    return {
        "message": "Registro exitoso",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    token = create_access_token({"sub": str(user.id), "role": user.role, "name": user.full_name})

    return {
        "message": "Login exitoso",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/me")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated user info."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")

    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }
