from fastapi import FastAPI
from app.database import engine, SessionLocal
from app.models.user import User
from app.utils.security import hash_password
from app.database import Base
from app.routes import auth
from app.utils.dependencies import get_current_user
from fastapi import Depends
from app.models import wallet
from app.routes import wallet as wallet_routes
from app.routes import vault as vault_routes



app = FastAPI()
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(wallet_routes.router, prefix="/wallet", tags=["Wallet"])
app.include_router(vault_routes.router, prefix="/vault", tags=["Vault"])

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def create_demo_users():
    db = SessionLocal()

    if not db.query(User).filter(User.email == "demo1@microyield.com").first():
        user1 = User(
            email="demo1@microyield.com",
            hashed_password=hash_password("password123")
        )
        db.add(user1)

    if not db.query(User).filter(User.email == "demo2@microyield.com").first():
        user2 = User(
            email="demo2@microyield.com",
            hashed_password=hash_password("password123")
        )
        db.add(user2)

    db.commit()
    db.close()

@app.get("/")
def root():
    return {"message": "MicroYield API running 🚀"}

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello {current_user}, you are authenticated."}

