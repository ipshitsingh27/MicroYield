from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.wallet import Wallet
from app.models.user import User
from app.services.stellar_service import generate_stellar_wallet
from app.utils.encryption import encrypt_secret
from app.utils.dependencies import get_current_user
from app.services.stellar_service import fund_testnet_account
from pydantic import BaseModel
from app.utils.encryption import decrypt_secret
from app.services.stellar_service import send_xlm
from app.utils.rounding import calculate_roundoff
from app.services.stellar_service import mint_usdc_to_vault
from app.config import VAULT_PUBLIC_KEY
from app.services.stellar_service import atomic_payment_with_roundoff


router = APIRouter()

@router.post("/create")
def create_wallet(current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()

    # Get user from DB
    user = db.query(User).filter(User.email == current_user).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Check if wallet already exists
    existing_wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if existing_wallet:
        db.close()
        return {
            "message": "Wallet already exists",
            "public_key": existing_wallet.public_key
        }

    # Generate new Stellar wallet
    wallet_data = generate_stellar_wallet()

    encrypted_secret = encrypt_secret(wallet_data["secret_key"])

    new_wallet = Wallet(
        user_id=user.id,
        public_key=wallet_data["public_key"],
        encrypted_secret=encrypted_secret
    )

    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    db.close()

    return {
        "message": "Wallet created successfully",
        "public_key": wallet_data["public_key"]
    }

@router.post("/fund")
def fund_wallet(current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    result = fund_testnet_account(wallet.public_key)

    db.close()
    return result

class SendRequest(BaseModel):
    destination: str
    amount: float

@router.post("/send")
def send_payment(data: SendRequest, current_user: str = Depends(get_current_user)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    decrypted_secret = decrypt_secret(wallet.encrypted_secret)

    result = send_xlm(
        source_secret=decrypted_secret,
        destination=data.destination,
        amount=data.amount
    )

    db.close()
    return result

@router.post("/pay")
def pay(
    destination: str,
    amount: float,
    roundoff_option: str,
    current_user: str = Depends(get_current_user),
):
    db: Session = SessionLocal()

    if roundoff_option not in ["none", "save", "invest"]:
        db.close()
        raise HTTPException(status_code=400, detail="Invalid roundoff option")

    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    decrypted_secret = decrypt_secret(wallet.encrypted_secret)

    # Calculate roundoff first
    if roundoff_option in ["save", "invest"]:
        roundoff_amount, rounded_total = calculate_roundoff(amount)
    else:
        roundoff_amount = 0
        rounded_total = amount

    # 🔥 Single atomic transaction
    payment_result = atomic_payment_with_roundoff(
        source_secret=decrypted_secret,
        merchant_destination=destination,
        merchant_amount=amount,
        vault_destination=VAULT_PUBLIC_KEY,
        roundoff_amount=roundoff_amount
    )

    # Record savings in DB only if roundoff happened
    if roundoff_amount > 0:
        # Mint USDC if invest selected
        if roundoff_option == "invest":
            mint_usdc_to_vault(roundoff_amount)

    db.commit()
    db.close()

    return {
        "payment_hash": payment_result["hash"],
        "roundoff_saved": roundoff_amount,
        "rounded_total": rounded_total,
        "option": roundoff_option,
        "message": "Atomic payment processed successfully"
    }