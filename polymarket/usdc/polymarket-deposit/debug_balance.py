
import re
def normalize_private_key(pk: str) -> str:
    if not pk:
        raise Exception("❌ PRIVATE KEY missing")
    pk = pk.strip()
    if pk.startswith("0x"):
        core = pk[2:]
    else:
        core = pk
    if not re.fullmatch(r"[0-9a-fA-F]{64}", core):
        raise Exception("❌ Invalid private key format")
    return "0x" + core

from web3 import Web3
from eth_account import Account
from config import RPC, USDC_CONTRACT(amount, decimals):
    try:
        return amount / (10 ** decimals)
    except Exception:
        return amount

def main():
    w3 = Web3(Web3.HTTPProvider(RPC))

    wallets_file = os.path.join(os.path.dirname(__file__), "wallets.txt")
    if not os.path.exists(wallets_file):
        print("wallets.txt not found in folder. Please add your private key or address there.")
        sys.exit(1)

    with open(wallets_file, 'r', encoding='utf-8') as f:
        first = next((line.strip() for line in f if line.strip()), None)

    if not first:
        print("No private key or address found in wallets.txt")
        sys.exit(1)

    # derive address if private key; otherwise accept address
    addr = None
    try:
        if first.startswith("0x") and len(first) == 66:  # private key length (0x + 64 hex)
            acct = Account.from_key(first)
            addr = acct.address
            print("Derived address from private key:", addr)
        elif first.startswith("0x") and len(first) == 42:  # address length
            addr = Web3.to_checksum_address(first)
            print("Using provided address:", addr)
        else:
            # try to parse as private key without 0x
            if len(first) == 64:
                acct = Account.from_key("0x" + first)
                addr = acct.address
                print("Derived address from private key (no 0x):", addr)
            else:
                raise ValueError("Unrecognized key/address format.")
    except Exception as e:
        print("Error deriving address from wallets.txt entry:", e)
        sys.exit(1)

    if not w3.is_connected():
        print("Web3 provider is NOT connected. Check your RPC:", RPC)
        sys.exit(1)

    try:
        native_balance = w3.eth.get_balance(addr)
        print("Web3 connected?:", True)
        print("Native balance (MATIC):", native_balance / 1e18)
    except Exception as e:
        print("Error fetching native balance:", e)
        sys.exit(1)

    # ERC20 minimal ABI (balanceOf, decimals, symbol)
    token = w3.eth.contract(address=w3.to_checksum_address(USDC_CONTRACT), abi=[
        {"constant": True, "inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
        {"constant": True, "inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
        {"constant": True, "inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
    ])

    try:
        decimals = token.functions.decimals().call()
        raw_balance = token.functions.balanceOf(addr).call()
        symbol = token.functions.symbol().call()
        print(f"Token: {symbol}")
        print("Token raw balance (units):", raw_balance)
        print("Token balance (human):", human_readable(raw_balance, decimals))
    except Exception as e:
        print("Error reading token balance:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
