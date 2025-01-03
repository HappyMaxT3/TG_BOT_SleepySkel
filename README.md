# 💀 SleepySkel — Telegram Bot to Track Your Sleep!

**SleepySkel** is a friendly skeleton bot that helps you track your sleep schedule, analyze your sleep quality, and gives tips to improve your rest. Let's get started!

---

## 🛠 Features:
- Track your sleep and wake-up times.
- Get tips to improve your sleep quality from SleepySkel (AI).
- Get some statistics.

---

## 📋 How to Install and Start the Bot

Follow the steps below to set up and run the **SleepySkel** bot on your device.

---

### ⚙️ 1. Clone the Project

First, download the bot to your device.

Run this command in your terminal:

```bash
git clone https://github.com/HappyMaxT3/TG_BOT_SleepySkel.git
```

Then, go to the project folder:

```bash
cd TG_BOT_SleepySkel
```

---

### 📄 2. Create the `config.py` File

Inside the `bot` folder, create a file called `config.py` and add the following lines:

```python
# config.py

BOT_TOKEN = "your_telegram_bot_token"
```

#### Where to get the tokens:
- **BOT_TOKEN**: Get it from [BotFather](https://t.me/botfather) in Telegram.

---

### 🖥️ 3. Create a Virtual Environment and Install Dependencies

1. Create a virtual environment in the project folder:

   ```bash
   # Windows
   python -m venv venv

   # MacOS / Linux
   python3 -m venv venv
   ```

2. Activate the virtual environment:

   ```bash
   # Windows
   venv\Scripts\activate

   # MacOS / Linux
   source venv/bin/activate
   ```

3. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

---

### 🚀 4. Start the Bot

After setting up everything, start the bot using the command:

```bash
# Windows
python -m bot.main

# MacOS / Linux
python3 -m bot.main
```

---

## 📚 Project Structure

Here’s what the project files look like:

```
TG_BOT_SleepySkel/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── commands.py
│   ├── handlers.py
│   ├── config.py
│   ├── states.py
│   ├── storage.py
│   ├── inline_handlers.py
│   └── model_interaction.py
├── requirements.txt
├── bot.db
└── README.md
```

---

## 🧩 Tips and Notes

- If OpenAI API is blocked in your country, use a VPN.
- Make sure the virtual environment is activated before running the bot.