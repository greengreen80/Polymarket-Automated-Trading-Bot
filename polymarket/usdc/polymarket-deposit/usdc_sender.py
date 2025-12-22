
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
from config import POLYMARKET_BRIDGE_CONTRACT, RPC, USDC_NATIVE_ADDRESS, USDC_BRIDGED_ADDRESS
import os

w3 = Web3(Web3.HTTPProvider(RPC))

USDC_ABI = [
    {"constant":False,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],
     "name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"_owner","type":"address"}],
     "name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"decimals",
     "outputs":[{"name":"","type":"uint8"}],"type":"function"},
]

def _contract(addr):
    try:
        return w3.eth.contract(address=w3.to_checksum_address(addr), abi=USDC_ABI)
    except Exception:
        return None

def get_token_and_balance(wallet):
    try:
        wallet = w3.to_checksum_address(wallet)
    except Exception:
        return None, 0, 6, "native"

    native = _contract(USDC_NATIVE_ADDRESS)
    bridged = _contract(USDC_BRIDGED_ADDRESS)

    bn_native = bn_bridged = 0
    dec_native = dec_bridged = 6

    try:
        if native:
            bn_native = int(native.functions.balanceOf(wallet).call())
            try:
                dec_native = int(native.functions.decimals().call())
            except Exception:
                dec_native = 6
    except Exception:
        bn_native = 0

    try:
        if bridged:
            bn_bridged = int(bridged.functions.balanceOf(wallet).call())
            try:
                dec_bridged = int(bridged.functions.decimals().call())
            except Exception:
                dec_bridged = 6
    except Exception:
        bn_bridged = 0

    # prefer higher non-zero balance, else native
    if bn_native >= bn_bridged and bn_native > 0:
        return native, bn_native, dec_native, "native"
    if bn_bridged > bn_native and bn_bridged > 0:
        return bridged, bn_bridged, dec_bridged, "bridged"
    return native, 0, dec_native, "native"

def extract_raw_tx(signed):
    # Direct handling for eth_account SignedTransaction variants
    for name in ("raw_transaction","rawTransaction","raw","raw_tx","serialized","signed_raw"):
        try:
            if hasattr(signed, name):
                v = getattr(signed, name)
                if v:
                    return v
        except Exception:
            pass
    # mapping-style
    if isinstance(signed, dict):
        for k in ("raw_transaction","rawTransaction","raw","raw_tx","raw_txn","serialized","signed_raw"):
            if k in signed and signed[k]:
                return signed[k]
    # __dict__ bytes fallback
    try:
        if hasattr(signed, "__dict__"):
            for k,v in signed.__dict__.items():
                if isinstance(v, (bytes, bytearray)) and len(v) > 0:
                    return v
    except Exception:
        pass
    return None

def send_all_usdc(private_key):
    try:
        acct = Account.from_key(private_key)
        sender = acct.address
    except Exception as e:
        print("[ERROR] invalid private key:", e)
        return

    contract, bal_raw, decimals, variant = get_token_and_balance(sender)
    human = bal_raw / (10 ** max(decimals,1))
    print(f"[INFO] wallet {sender} raw={bal_raw} decimals={decimals} human={human:,.6f}")

    if bal_raw == 0:
        print(f"[SKIP] {sender} → No USDC (native or bridged)")
        return

    if contract is None:
        print(f"[ERROR] contract instance not available for variant={variant}")
        return

    dest = w3.to_checksum_address(POLYMARKET_BRIDGE_CONTRACT)
    print(f"[SEND] {sender} → {dest} | USDC: {human:,.6f} (using {variant})")

    try:
        nonce = w3.eth.get_transaction_count(sender)
    except Exception as e:
        print("[ERROR] get_transaction_count failed:", e)
        return

    try:
        gas_est = contract.functions.transfer(dest, bal_raw).estimate_gas({"from": sender})
    except Exception:
        gas_est = 150000

    tx = contract.functions.transfer(dest, bal_raw).build_transaction({
        "from": sender,
        "nonce": nonce,
        "gas": gas_est,
        "gasPrice": w3.eth.gas_price
    })

    # ensure chainId if available
    try:
        cid = w3.eth.chain_id
        if cid:
            tx.setdefault("chainId", cid)
    except Exception:
        pass

    # sign (try eth_account then web3 fallback)
    signed = None
    try:
        signed = Account.sign_transaction(tx, private_key)
    except Exception as e1:
        try:
            signed = w3.eth.account.sign_transaction(tx, private_key)
        except Exception as e2:
            print("[ERROR] signing failed (Account + w3.eth.account):", e1, e2)
            return

    raw_tx = extract_raw_tx(signed)
    if raw_tx is None:
        print("[ERROR] could not extract raw transaction (signed type: %s)" % type(signed))
        # attempt best-effort debug (no secrets)
        try:
            if isinstance(signed, dict):
                print("[DEBUG] signed keys:", list(signed.keys())[:40])
            else:
                print("[DEBUG] signed dir sample:", [n for n in dir(signed) if not n.startswith('_')][:60])
        except Exception:
            pass
        return

    try:
        tx_hash = w3.eth.send_raw_transaction(raw_tx)
    except Exception as e:
        print("[ERROR] send_raw_transaction failed:", e)
        return

    try:
        print("TX HASH:", w3.to_hex(tx_hash))
    except Exception:
        try:
            print("TX HASH (fallback):", tx_hash.hex())
        except Exception:
            print("TX HASH (fallback):", str(tx_hash))
