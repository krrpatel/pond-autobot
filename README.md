# 🤖 CryptoPond Auto Bot

An intelligent automation bot for [CryptoPond.xyz](https://cryptopond.xyz) that:

- 🧠 Automatically generates and submits a new crypto project idea **once per day** using **Gemini AI**.
- 🗳️ Automatically votes on unvoted ideas **every 2 days**.
- 📆 Stores configuration in a `config.json` file after the first run.
- 📉 Fetches and displays your CryptoPond **points** summary.
- ⏰ Runs continuously and schedules actions using local time.

---

## 🔧 Features

- AI-generated ideas with `name`, `subtitle`, and `descriptio`n
- 24h/48h timers for posting and voting respectively
- Tracks last action timestamps using `config.json`
- Uses official CryptoPond API endpoints
- Easy to set up and run

---

## 🧱 Requirements

- Python 3.8+
- Packages:
  - `requests`
  - `schedule`
  - `google-generativeai`

---

## 🚀 Setup & Run

### 1 . Clone the repository

```bash
git clone https://github.com/krrpatel/pond-autobot.git
cd cryptopond-auto-bot
```

### 2 . enable venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3 . Install dependencies:

```bash
pip install requests schedule google-generativeai
```

### 4 . start

```bash
python3 main.py
```

📝 On first run, you'll be prompted for:

- Developer ID
- CryptoPond Auth Token (JWT)
- Gemini API Key

This info is saved in `config.json`.

---

## 🗓️ Action Schedule

| Action        | Frequency | Triggered Immediately on First Run? |
| ------------- | --------- | ----------------------------------- |
| Post Idea     | Every 24h | ✅ Yes                               |
| Vote on Ideas | Every 48h | ✅ Yes                               |

---

## 📈 Points Tracking

Each time the bot runs (for post or vote), it fetches and shows:

- 🪙 Today’s Points
- 📅 Monthly Points
- 🧮 Total Points

---

## 🔐 Config File Format (`config.json`)

```json
{
  "developer_id": "YOUR_ID",
  "auth_token": "YOUR_AUTH_TOKEN",
  "gemini_api_key": "YOUR_GEMINI_KEY",
  "last_post_time": "ISO_TIMESTAMP",
  "last_vote_time": "ISO_TIMESTAMP"
}
```

---

## ✅ Sample Output

```
🗖️ Posting idea at 2025-06-30 12:00:00
📌 ChainGuard - Secure Web3 Alerts
📝 A decentralized platform for smart contract anomaly alerts and transaction tracking.

🗖️ Voting at 2025-06-30 12:00:00
🗳️ Voting on: QuantumMesh Ledger (ID: 12345)
✅ Success
💰 Points Summary: Today: 55 | Month: 200 | Total: 500
```

---

## 📜 License

This project is licensed under the MIT License.
