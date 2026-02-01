from decimal import Decimal, ROUND_DOWN
from typing import List, Dict
from datetime import datetime

from app.services.stellar_service import (
    soroban_get_total_usdc_principal,
    soroban_get_user_summary,
    soroban_add_yield_admin
)

# Annual APY (8%)
ANNUAL_APY = Decimal("0.08")
DAYS_IN_YEAR = Decimal("365")


def calculate_daily_yield(total_principal: Decimal) -> Decimal:
    """
    Simulate daily yield based on annual APY.
    """
    daily_rate = ANNUAL_APY / DAYS_IN_YEAR
    earned = total_principal * daily_rate
    return earned.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)


def distribute_daily_yield(users: List[str]) -> Dict:
    """
    Distribute yield proportionally to all users
    based on their USDC principal.
    """

    total_principal = Decimal(
        soroban_get_total_usdc_principal()
    )

    if total_principal == 0:
        return {"message": "No principal in vault"}

    daily_yield = calculate_daily_yield(total_principal)

    results = []

    for user_public_key in users:
        xlm, principal, yield_amt = soroban_get_user_summary(user_public_key)

        user_principal = Decimal(principal)

        if user_principal == 0:
            continue

        share_ratio = user_principal / total_principal
        user_yield = (daily_yield * share_ratio).quantize(
            Decimal("0.0000001"),
            rounding=ROUND_DOWN
        )

        if user_yield > 0:
            soroban_add_yield_admin(user_public_key, int(user_yield))
            results.append({
                "user": user_public_key,
                "yield_added": str(user_yield)
            })

    return {
        "total_principal": str(total_principal),
        "daily_yield_generated": str(daily_yield),
        "distributed_to": results,
        "timestamp": datetime.utcnow().isoformat()
    }