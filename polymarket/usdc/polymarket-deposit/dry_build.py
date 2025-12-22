
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
from config import RPC, USDC_CONTRACT= Web3(Web3.HTTPProvider(RPC))

with open("wallets.txt") as f:
    priv = next(line.strip() for line in f if line.strip())

acct = Account.from_key(priv)
sender = acct.address

token = w3.eth.contract(address=w3.to_checksum_address(USDC_CONTRACT), abi=[
    {"constant": True, "inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant": False, "inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}
])

bal = token.functions.balanceOf(w3.to_checksum_address(sender)).call()
cold = w3.to_checksum_address(POLYMARKET_BRIDGE_CONTRACT)
nonce = w3.eth.get_transaction_count(sender)

tx = token.functions.transfer(cold, bal).build_transaction({
    "from": sender,
    "nonce": nonce,
    "gas": 100000,
    "gasPrice": w3.eth.gas_price
})

print("DRY BUILD: nonce:", nonce)
print("DRY BUILD: tx:", tx)
print("DRY BUILD: gasPrice (wei):", w3.eth.gas_price)
print("DRY BUILD: token balance (units):", bal)
