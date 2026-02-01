import requests
from stellar_sdk import Server, TransactionBuilder, Network, Asset, Keypair, Address
from app.config import HORIZON_URL
from app.config import ISSUER_PUBLIC_KEY, VAULT_SECRET_KEY
from app.config import (
    ISSUER_SECRET_KEY,
    ISSUER_PUBLIC_KEY,
    VAULT_PUBLIC_KEY,
)
from stellar_sdk import Address
from decimal import Decimal, ROUND_DOWN
from app.config import SOROBAN_CONTRACT_ID, SOROBAN_RPC_URL
from stellar_sdk import contract
from stellar_sdk import Server as SorobanServer

server = Server(HORIZON_URL)

def generate_stellar_wallet():
    keypair = Keypair.random()

    return {
        "public_key": keypair.public_key,
        "secret_key": keypair.secret
    }

def fund_testnet_account(public_key: str):
    response = requests.get(
        f"https://friendbot.stellar.org?addr={public_key}"
    )
    return response.json()

def send_xlm(source_secret: str, destination: str, amount: Decimal):
    source_keypair = Keypair.from_secret(source_secret)
    source_account = server.load_account(source_keypair.public_key)

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100
        )
        .append_payment_op(
            destination=destination,
            amount=str(amount.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)),
            asset=Asset.native()
        )
        .set_timeout(30)
        .build()
    )

    transaction.sign(source_keypair)
    response = server.submit_transaction(transaction)

    return {
        "successful": response["successful"],
        "hash": response["hash"]
    }
    
def create_vault_trustline():
    vault_keypair = Keypair.from_secret(VAULT_SECRET_KEY)
    source_account = server.load_account(vault_keypair.public_key)

    usdc_asset = Asset("USDC", ISSUER_PUBLIC_KEY)

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100
        )
        .append_change_trust_op(asset=usdc_asset)
        .set_timeout(30)
        .build()
    )

    transaction.sign(vault_keypair)
    response = server.submit_transaction(transaction)

    return {
        "successful": response["successful"],
        "hash": response["hash"]
    }
    
def mint_usdc_to_vault(amount: Decimal):
    issuer_keypair = Keypair.from_secret(ISSUER_SECRET_KEY)
    server = Server("https://horizon-testnet.stellar.org")

    source_account = server.load_account(issuer_keypair.public_key)

    usdc_asset = Asset("USDC", ISSUER_PUBLIC_KEY)

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_payment_op(
            destination=VAULT_PUBLIC_KEY,
            amount=str(amount),
            asset=usdc_asset,
        )
        .set_timeout(30)
        .build()
    )

    transaction.sign(issuer_keypair)
    response = server.submit_transaction(transaction)

    return {
        "successful": response["successful"],
        "hash": response["hash"],
    }
    
def atomic_payment_with_roundoff(
    source_secret: str,
    merchant_destination: str,
    merchant_amount: Decimal,
    vault_destination: str,
    roundoff_amount: Decimal,
):
    source_keypair = Keypair.from_secret(source_secret)
    source_account = server.load_account(source_keypair.public_key)

    transaction = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=100,
    )

    # Payment to merchant
    transaction.append_payment_op(
        destination=merchant_destination,
        amount=str(merchant_amount.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)),
        asset=Asset.native()
    )

    # Payment to vault (roundoff)
    if roundoff_amount > 0:
        transaction.append_payment_op(
            destination=vault_destination,
            amount=str(roundoff_amount.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)),
            asset=Asset.native()
        )

    transaction = transaction.set_timeout(30).build()

    transaction.sign(source_keypair)

    try:
        response = server.submit_transaction(transaction)
    except Exception as e:
        return {
            "successful": False,
            "error": str(e)
        }

    return {
        "successful": response["successful"],
        "hash": response["hash"]
    }

def soroban_deposit(user_secret: str, amount: int):
    soroban_server = SorobanServer(SOROBAN_RPC_URL)

    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.get_account(keypair.public_key)

    contract = contract(SOROBAN_CONTRACT_ID)

    transaction = (
        soroban_server.prepare_transaction(
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_operation(
                contract.call(
                    "deposit",
                    Address.from_account_id(keypair.public_key),
                    amount
                )
            )
            .set_timeout(30)
            .build()
        )
    )

    transaction.sign(keypair)

    response = soroban_server.send_transaction(transaction)

    return {
        "hash": response.hash,
        "status": response.status
    }
    
def soroban_withdraw(user_secret: str, amount: int):
    soroban_server = SorobanServer(SOROBAN_RPC_URL)

    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.get_account(keypair.public_key)

    contract = contract(SOROBAN_CONTRACT_ID)

    transaction = (
        soroban_server.prepare_transaction(
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_operation(
                contract.call(
                    "withdraw",
                    keypair.public_key,
                    amount
                )
            )
            .set_timeout(30)
            .build()
        )
    )

    transaction.sign(keypair)

    response = soroban_server.send_transaction(transaction)

    return {
        "hash": response.hash,
        "status": response.status
    }

def soroban_get_balance(user_public_key: str):
    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract = contract(SOROBAN_CONTRACT_ID)

    source_account = soroban_server.get_account(user_public_key)

    tx = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=100,
    ).append_operation(
        contract.call("get_balance", user_public_key)
    ).set_timeout(30).build()

    simulation = soroban_server.simulate_transaction(tx)

    return simulation.result

def soroban_get_total_usdc_principal():
    from stellar_sdk import SorobanServer, Contract, Network
    from stellar_sdk import TransactionBuilder

    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract = Contract(SOROBAN_CONTRACT_ID)

    source_account = soroban_server.get_account(VAULT_PUBLIC_KEY)

    tx = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=100,
    ).append_operation(
        contract.call("total_usdc_principal")
    ).set_timeout(30).build()

    simulation = soroban_server.simulate_transaction(tx)

    return simulation.result.retval

def soroban_get_user_summary(user_public_key: str):
    from stellar_sdk import SorobanServer, Contract, Network
    from stellar_sdk import TransactionBuilder

    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract = Contract(SOROBAN_CONTRACT_ID)

    source_account = soroban_server.get_account(user_public_key)

    tx = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=100,
    ).append_operation(
        contract.call("get_user_summary", user_public_key)
    ).set_timeout(30).build()

    simulation = soroban_server.simulate_transaction(tx)

    return simulation.result.retval

def soroban_add_yield_admin(user_public_key: str, amount: int):
    from stellar_sdk import SorobanServer, Contract, Network, Keypair, Address
    from stellar_sdk import TransactionBuilder

    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract = Contract(SOROBAN_CONTRACT_ID)

    admin_keypair = Keypair.from_secret(VAULT_SECRET_KEY)
    source_account = soroban_server.get_account(admin_keypair.public_key)

    transaction = soroban_server.prepare_transaction(
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_operation(
            contract.call(
                "add_yield",
                Address.from_account_id(user_public_key),
                amount
            )
        )
        .set_timeout(30)
        .build()
    )

    transaction.sign(admin_keypair)

    response = soroban_server.send_transaction(transaction)

    return response.status
