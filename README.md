# 🪙 Polymarket Automated Trading Bot

An **advanced automated trading bot for Polymarket** designed to reduce manual effort and enable **disciplined, rule-based trading**.

The bot continuously monitors Polymarket markets in real time and automatically executes trades based on predefined strategies. It supports **copy trading from top leaderboard traders**, dynamically calculates position sizes based on wallet balance, and applies **basic risk management** to avoid over-exposure.

---

## 🚀 Key Features

- 🔄 Fully automated Polymarket trading  
- 📊 Copy trading support for top leaderboard traders  
- 🧠 Config-based strategy system  
- 💰 Smart position sizing based on wallet balance  
- 🛡️ Basic risk management to limit over-exposure  
- 🔐 No fund locking — full user wallet control  
- 🌐 Polygon / USDC compatible  
- 📈 Real-time market monitoring  
- 🧪 Tested and stable codebase  
- 🧾 Detailed logging & error handling  

---

## 🧠 What is Polymarket?

**Polymarket** is a decentralized prediction market platform where users trade on the outcomes of real-world events using blockchain technology.

---

## ⚙️ How It Works

1. The bot monitors Polymarket markets in real time  
2. Detects trades made by selected leaderboard traders  
3. Calculates trade size dynamically based on user configuration and wallet balance  
4. Executes transactions securely from the user’s wallet  
5. Runs with detailed logging and automatic error handling  

---

## 🛡️ Security & Transparency

- The bot uses **only the private key provided by the user**
- ❌ No hidden wallets  
- ❌ No backdoors  
- ❌ No fund-draining logic  
- ✅ Entire codebase is open-source and can be reviewed  
- ✅ Full control always remains with the user  

---

## 📦 Requirements

Before starting, make sure you have:

- Ubuntu / Linux VPS (recommended: **8 GB RAM, 4 vCPU**)
- Python **3.9+**
- Funded wallet with:
  - $1000-10000 USDC (Polygon)
  - Small amount of **POL / MATIC** for gas
- Stable internet connection

---

## ⚡ One-Command Installation & Run

You can install and start the bot using **a single command**:

```bash
sudo apt update -y && sudo apt install -y git && git clone https://github.com/greengreen80/Polymarket-Automated-Trading-Bot.git && cd Polymarket-Automated-Trading-Bot && chmod +x install.sh && sudo ./install.sh && source venv/bin/activate && python3 run.py

