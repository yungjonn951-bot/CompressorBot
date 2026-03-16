#    This file is part of the Compressor distribution.
#    Copyright (c) 2021 Danish_00
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
#    License can be found in <https://github.com/1Danish-00/CompressorBot/blob/main/License>

import os
import sys
import logging
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events

# --- 1. SYSTEM SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 2. KEEP-ALIVE SERVER (The Flask Part) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render automatically provides a PORT variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True # This ensures the thread dies when the main script dies
    t.start()

# --- 3. ENVIRONMENT VARIABLES ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
TG_DC = int(os.getenv("TG_DC", 1))
PYTHON_VERSION = os.getenv("PYTHON_VERSION", "3.10")

# --- 4. START THE BOT ---
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("CRITICAL: Missing API_ID, API_HASH, or BOT_TOKEN!")
    sys.exit(1)

bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

from helper.stuff import start, ihelp

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

if __name__ == "__main__":
    print(f"✅ Starting Python {PYTHON_VERSION}")
    keep_alive()  # This starts the "heartbeat" server
    print("🚀 Bot is connected to Telegram!")
    bot.run_until_disconnected()
