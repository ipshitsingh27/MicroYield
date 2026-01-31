from fastapi import APIRouter
from app.yield_engine.yield_logic import simulate_liquidity_usage, calculate_user_balance

router = APIRouter(prefix="/yield", tags=["Yield"])

@router.post("/simulate")
def simulate_yield():
    return simulate_liquidity_usage()

@router.get("/balance/{shares}")
def get_user_balance(shares: float):
    return {"user_balance": calculate_user_balance(shares)}
