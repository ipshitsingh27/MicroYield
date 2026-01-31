from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from datetime import datetime
from app.database import Base

class VaultDeposit(Base):
    __tablename__ = "vault_deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)