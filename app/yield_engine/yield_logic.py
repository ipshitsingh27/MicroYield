from datetime import datetime

# Vault state placeholder
vault_state = {
    "total_usdc": 0.0,
    "total_shares": 0.0,
    "last_updated": datetime.utcnow(),
}

def simulate_liquidity_usage():
    """
    Simulate companies using the vault and earning fees.
    """
    # SAFE demo APY — adjust later
    DAILY_APY = 0.08
    daily_rate = DAILY_APY / 365

    earned_usdc = vault_state["total_usdc"] * daily_rate
    vault_state["total_usdc"] += earned_usdc
    vault_state["last_updated"] = datetime.utcnow()

    return {
        "earned_today": round(earned_usdc, 4),
        "vault_balance": round(vault_state["total_usdc"], 4),
    }

def calculate_user_balance(user_shares: float):
    """
    Calculate a user's balance based on shares.
    """
    if vault_state["total_shares"] == 0:
        return 0.0

    share_value = vault_state["total_usdc"] / vault_state["total_shares"]
    return round(user_shares * share_value, 4)
