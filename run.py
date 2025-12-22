import time
import os
import sys

# add inner folder to python import path so imports like `from usdc_sender import ...` work
ROOT = os.path.dirname(__file__)
INNER = os.path.join(ROOT, "polymarket", "usdc", "polymarket-deposit")
if INNER not in sys.path:
    sys.path.insert(0, INNER)

from usdc_sender import send_all_usdc

# wallets file is stored inside polymarket/usdc/polymarket-deposit per project layout
WALLETS_PATH = os.path.join(INNER, "wallets.txt")

def main():
    if not os.path.exists(WALLETS_PATH):
        print("Wallets file not found at:", WALLETS_PATH)
        return

    with open(WALLETS_PATH) as f:
        keys = [x.strip() for x in f if x.strip()]

    print(f"Total wallets loaded: {len(keys)}")

    for key in keys:
        send_all_usdc(key)
        time.sleep(1)

if __name__ == "__main__":
    main()
