from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import LoginRequest
from app.utils.security import verify_password
from app.services.auth_service import create_access_token

router = APIRouter()

@router.post("/login")
def login(data: LoginRequest):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})

    db.close()
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
