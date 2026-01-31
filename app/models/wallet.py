from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    public_key = Column(String, unique=True, index=True)
    encrypted_secret = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
