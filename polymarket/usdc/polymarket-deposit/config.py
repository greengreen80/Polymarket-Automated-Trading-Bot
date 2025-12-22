
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

# --- AUTO-DETECT USDC CONTRACT (injected) ---
import os
from web3 import Web3
from eth_account import Account

USDC_NATIVE_ADDRESS = os.getenv('USDC_NATIVE_ADDRESS', '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359')
USDC_BRIDGED_ADDRESS = os.getenv('USDC_BRIDGED_ADDRESS', '0x2791bca1f2de4661ed88a30c99a7a9449aa84174')
RPC = os.getenv('RPC', 'https://polygon-rpc.com')
AUTO_DETECT_WALLET = os.getenv('AUTO_DETECT_WALLET', os.getenv('WALLET_ADDRESS', ''))

def _normalize_wallet_line(line):
    ln = line.strip()
    if not ln:
        return None
    try:
        if ln.startswith('0x') and len(ln) == 66:
            acct = Account.from_key(ln)
            return acct.address
    except Exception:
        pass
    return ln

def _auto_select_usdc():
    if os.getenv('USDC_ADDRESS'):
        return os.getenv('USDC_ADDRESS')
    sel = os.getenv('USDC_SELECTED', '').lower()
    if sel == 'bridged':
        return USDC_BRIDGED_ADDRESS
    if sel == 'native':
        return USDC_NATIVE_ADDRESS
    try:
        w3 = Web3(Web3.HTTPProvider(RPC))
        wallets = []
        if AUTO_DETECT_WALLET:
            wallets = [_normalize_wallet_line(AUTO_DETECT_WALLET)]
        else:
            p = os.path.join(os.path.dirname(__file__), "wallets.txt")
            if os.path.exists(p):
                with open(p,'r') as f:
                    for ln in f:
                        addr = _normalize_wallet_line(ln)
                        if addr:
                            wallets.append(addr)
        wallets = [w for w in wallets if w]
        if not wallets:
            return USDC_NATIVE_ADDRESS
        ERC20_MIN_ABI = [
            {"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
        ]
        c_native = w3.eth.contract(address=w3.to_checksum_address(USDC_NATIVE_ADDRESS), abi=ERC20_MIN_ABI)
        c_bridged = w3.eth.contract(address=w3.to_checksum_address(USDC_BRIDGED_ADDRESS), abi=ERC20_MIN_ABI)
        total_native = 0
        total_bridged = 0
        for addr in wallets:
            try:
                a = w3.to_checksum_address(addr)
            except Exception:
                continue
            try:
                total_native += int(c_native.functions.balanceOf(a).call())
            except Exception:
                pass
            try:
                total_bridged += int(c_bridged.functions.balanceOf(a).call())
            except Exception:
                pass
        if total_native > total_bridged and total_native > 0:
            return USDC_NATIVE_ADDRESS
        if total_bridged > total_native and total_bridged > 0:
            return USDC_BRIDGED_ADDRESS
    except Exception:
        pass
    return USDC_NATIVE_ADDRESS

USDC_ADDRESS = _auto_select_usdc()
USDC_CONTRACT = os.getenv('USDC_ADDRESS', USDC_ADDRESS)
# --- end auto-detect injection ---

# --- AUTO-DETECT USDC CONTRACT (injected) ---
import os
from web3 import Web3
from eth_account import Account

# Known USDC addresses on Polygon (native / bridged)
USDC_NATIVE_ADDRESS = os.getenv('USDC_NATIVE_ADDRESS', '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359')
USDC_BRIDGED_ADDRESS = os.getenv('USDC_BRIDGED_ADDRESS', '0x2791bca1f2de4661ed88a30c99a7a9449aa84174')

# RPC to use for detection — set RPC env if you have a provider
RPC = os.getenv('RPC', 'https://polygon-rpc.com')

# For auto-detect: public wallet address to check balances for.
# If you have many wallets, you can list them in wallets.txt (one per line).
AUTO_DETECT_WALLET = os.getenv('AUTO_DETECT_WALLET', os.getenv('WALLET_ADDRESS', ''))

def _normalize_wallet_line(line):
    ln = line.strip()
    if not ln:
        return None
    # If it looks like a private key (0x + 64 hex chars), convert to address
    try:
        if ln.startswith('0x') and len(ln) == 66:
            acct = Account.from_key(ln)
            return acct.address
    except Exception:
        pass
    # otherwise assume it's an address
    return ln

def _auto_select_usdc():
    # If user explicitly sets USDC_ADDRESS env, prefer that (backwards compatible)
    if os.getenv('USDC_ADDRESS'):
        return os.getenv('USDC_ADDRESS')

    # If user set USDC_SELECTED env, prefer that
    sel = os.getenv('USDC_SELECTED', '').lower()
    if sel == 'bridged':
        return USDC_BRIDGED_ADDRESS
    if sel == 'native':
        return USDC_NATIVE_ADDRESS

    # Else try automatic detection: check balances on chain
    try:
        w3 = Web3(Web3.HTTPProvider(RPC))

        wallets = []
        if AUTO_DETECT_WALLET:
            wallets = [_normalize_wallet_line(AUTO_DETECT_WALLET)]
        else:
            # fallback: read wallets.txt (lines may be addresses or private keys)
            try:
                p = os.path.join(os.path.dirname(__file__), "wallets.txt")
                if os.path.exists(p):
                    with open(p,'r') as f:
                        for ln in f:
                            addr = _normalize_wallet_line(ln)
                            if addr:
                                wallets.append(addr)
            except Exception:
                pass

        # filter invalid
        wallets = [w for w in wallets if w]

        # If no wallet to check, fallback to native
        if not wallets:
            return USDC_NATIVE_ADDRESS

        # Minimal ABI for balanceOf
        ERC20_MIN_ABI = [
            {"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
        ]

        c_native = w3.eth.contract(address=w3.to_checksum_address(USDC_NATIVE_ADDRESS), abi=ERC20_MIN_ABI)
        c_bridged = w3.eth.contract(address=w3.to_checksum_address(USDC_BRIDGED_ADDRESS), abi=ERC20_MIN_ABI)

        total_native = 0
        total_bridged = 0
        for addr in wallets:
            try:
                a = w3.to_checksum_address(addr)
            except Exception:
                continue
            try:
                b_native = c_native.functions.balanceOf(a).call()
            except Exception:
                b_native = 0
            try:
                b_bridged = c_bridged.functions.balanceOf(a).call()
            except Exception:
                b_bridged = 0
            total_native += int(b_native)
            total_bridged += int(b_bridged)

        # If any non-zero, pick the higher one
        if total_native > total_bridged and total_native > 0:
            return USDC_NATIVE_ADDRESS
        if total_bridged > total_native and total_bridged > 0:
            return USDC_BRIDGED_ADDRESS

    except Exception as e:
        # detection failed for some reason (RPC down, bad RPC, etc) — fall back
        print("[USDC-AUTO-DETECT] detection failed:", e)

    # final fallback
    return USDC_NATIVE_ADDRESS

# Compute final USDC address
USDC_ADDRESS = _auto_select_usdc()
# Backwards compatibility alias used in project
USDC_CONTRACT = os.getenv('USDC_ADDRESS', USDC_ADDRESS)
# --- end auto-detect injection ---


import os
from web3 import Web3

# Known USDC addresses on Polygon (native / bridged)
USDC_NATIVE_ADDRESS = os.getenv('USDC_NATIVE_ADDRESS', '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359')
USDC_BRIDGED_ADDRESS = os.getenv('USDC_BRIDGED_ADDRESS', '0x2791bca1f2de4661ed88a30c99a7a9449aa84174')

# RPC to use for detection — set RPC in env or keep default below
RPC = os.getenv('RPC', 'https://polygon-rpc.com')

# Address to check balances for (public address). You can set one address, or set AUTO_DETECT_WALLETS_FILE
# Option A: single address
AUTO_DETECT_WALLET = os.getenv('AUTO_DETECT_WALLET', os.getenv('WALLET_ADDRESS', ''))

def _auto_select_usdc():
    # If user explicitly sets USDC_ADDRESS env, prefer that (backwards compatible)
    if os.getenv('USDC_ADDRESS'):
        return os.getenv('USDC_ADDRESS')

    # If user set USDC_SELECTED env, prefer that
    sel = os.getenv('USDC_SELECTED', '').lower()
    if sel == 'bridged':
        return USDC_BRIDGED_ADDRESS
    if sel == 'native':
        return USDC_NATIVE_ADDRESS

    # Else try automatic detection: check balances on chain
    try:
        w3 = Web3(Web3.HTTPProvider(RPC))
        # choose wallets to check
        wallets = []
        if AUTO_DETECT_WALLET:
            wallets = [AUTO_DETECT_WALLET]
        else:
            # fallback: try reading wallets.txt if present (addresses, not private keys)
            try:
                p = os.path.join(os.path.dirname(__file__), "wallets.txt")
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        for ln in f:
                            ln = ln.strip()
                            if ln and not ln.lower().startswith('#'):
                                wallets.append(ln)
            except Exception:
                pass

        # If no wallet to check, fallback to native
        if not wallets:
            return USDC_NATIVE_ADDRESS

        # Minimal ABI for balanceOf
        ERC20_MIN_ABI = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
                         {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]

        c_native = w3.eth.contract(address=w3.to_checksum_address(USDC_NATIVE_ADDRESS), abi=ERC20_MIN_ABI)
        c_bridged = w3.eth.contract(address=w3.to_checksum_address(USDC_BRIDGED_ADDRESS), abi=ERC20_MIN_ABI)

        # For each wallet, check balances and pick the contract with largest combined balance across wallets
        total_native = 0
        total_bridged = 0
        for addr in wallets:
            try:
                a = w3.to_checksum_address(addr)
            except Exception:
                continue
            try:
                b_native = c_native.functions.balanceOf(a).call()
            except Exception:
                b_native = 0
            try:
                b_bridged = c_bridged.functions.balanceOf(a).call()
            except Exception:
                b_bridged = 0
            total_native += int(b_native)
            total_bridged += int(b_bridged)

        # If any non-zero, pick the higher one
        if total_native > total_bridged and total_native > 0:
            return USDC_NATIVE_ADDRESS
        if total_bridged > total_native and total_bridged > 0:
            return USDC_BRIDGED_ADDRESS

    except Exception as e:
        # detection failed for some reason (RPC down, bad RPC, etc) — fall back
        print("[USDC-AUTO-DETECT] detection failed:", e)

    # final fallback
    return USDC_NATIVE_ADDRESS

# Compute final USDC address
USDC_ADDRESS = _auto_select_usdc()
# Backwards compatibility alias used in project
USDC_CONTRACT = os.getenv('USDC_ADDRESS', USDC_ADDRESS)
# --- end auto-detect injection ---




import os
# Default Polygon Mainnet RPC
RPC = "https://polygon-rpc.com"
POLYMARKET_BRIDGE_CONTRACT = "0xe12cF0fd88225A486634c0EBcf0DCc404e23F949"
# Default USDC contract on Polygon
USDC_CONTRACT = os.getenv('USDC_ADDRESS', USDC_ADDRESS)
