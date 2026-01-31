from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from app.utils.dependencies import get_current_user
from app.utils.encryption import decrypt_secret
from app.services.stellar_service import send_xlm
from app.config import VAULT_PUBLIC_KEY, VAULT_SECRET_KEY
from app.services.stellar_service import create_vault_trustline
from app.services.stellar_service import mint_usdc_to_vault
from app.services.stellar_service import soroban_deposit
from app.services.stellar_service import soroban_withdraw
from app.services.stellar_service import soroban_get_balance


router = APIRouter()

@router.post("/deposit")
def deposit_to_vault(amount: float, current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    decrypted_secret = decrypt_secret(wallet.encrypted_secret)

    # 1️⃣ Move XLM to vault
    send_result = send_xlm(
        source_secret=decrypted_secret,
        destination=VAULT_PUBLIC_KEY,
        amount=amount
    )

    # 2️⃣ Update smart contract state
    contract_result = soroban_deposit(decrypted_secret, int(amount))

    db.close()

    return {
        "xlm_transfer_hash": send_result["hash"],
        "contract_tx_hash": contract_result["hash"],
        "amount": amount,
        "message": "Deposit successful"
    }

@router.get("/my-balance")
def my_vault_balance(current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    balance = soroban_get_balance(wallet.public_key)

    db.close()

    return {
        "on_chain_vault_balance": balance
    }
    
@router.post("/setup-trustline")
def setup_trustline():
    return create_vault_trustline()

@router.post("/mint-usdc")
def mint_usdc(amount: float):
    return mint_usdc_to_vault(amount)

from app.services.stellar_service import soroban_withdraw

@router.post("/withdraw")
def withdraw_from_vault(amount: float, current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    decrypted_secret = decrypt_secret(wallet.encrypted_secret)

    # 1️⃣ Reduce contract balance
    contract_result = soroban_withdraw(decrypted_secret, int(amount))

    # 2️⃣ Send XLM from vault to user
    vault_send = send_xlm(
        source_secret=VAULT_SECRET_KEY,
        destination=wallet.public_key,
        amount=amount
    )

    db.close()

    return {
        "contract_tx_hash": contract_result["hash"],
        "xlm_transfer_hash": vault_send["hash"],
        "amount": amount,
        "message": "Withdraw successful"
    }
