#!/bin/bash
echo "============================================"
echo "      POLYMARKET BOT INSTALLER"
echo "============================================"
echo ""

if ! command -v python3 &> /dev/null
then
    echo "Python3 not found! Install Python3 first."
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/4] Installing Python dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install web3 eth-account python-dotenv >/dev/null 2>&1

INNER_DIR="$(pwd)/polymarket/usdc/polymarket-deposit"
mkdir -p "$INNER_DIR"

echo ""
echo "[3/4] Asking for PRIVATE KEY only..."
read -p "Enter PRIVATE KEY (0x....): " PK

if [[ -z "$PK" ]]; then
    echo "ERROR: Private key cannot be empty."
    exit 1
fi

echo "$PK" > "$INNER_DIR/wallets.txt"
chmod 600 "$INNER_DIR/wallets.txt"
echo "Private key saved to $INNER_DIR/wallets.txt"

echo ""
echo "[4/4] Installation complete!"
echo ""
echo "To RUN the bot:"
echo "----------------------------------"
echo "source venv/bin/activate"
echo "python3 run.py"
echo "----------------------------------"
