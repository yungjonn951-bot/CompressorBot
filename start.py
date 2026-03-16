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
from motor.motor_asyncio import AsyncIOMotorClient

# --- 1. SYSTEM & LOGGING SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. RENDER KEEP-ALIVE (FLASK) ---
app = Flask('')

@app.route('/')
def home():
    return "PrivComBot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 3. ENVIRONMENT VARIABLES ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
MONGO_URI = os.getenv("MONGO_URI")
PYTHON_VERSION = os.getenv("PYTHON_VERSION", "3.10")

# --- 4. SAFETY CHECK ---
if not all([API_ID, API_HASH, BOT_TOKEN, MONGO_URI]):
    logger.error("❌ MISSING CRITICAL VARS: Check API_ID, API_HASH, BOT_TOKEN, and MONGO_URI in Render!")
    sys.exit(1)

# --- 5. INITIALIZE CLIENTS (TELEGRAM & MONGO) ---
bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

# Import logic from helper/stuff.py
try:
    from helper.stuff import start, ihelp, broadcast, add_user
except ImportError:
    logger.error("❌ Could not find helper/stuff.py! Ensure the folder exists.")

# --- 6. COMMAND HANDLERS ---

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # Saves user to MongoDB via the helper function
    await add_user(event.sender_id)
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

@bot.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_handler(event):
    # Only the owner can broadcast
    await broadcast(event, bot, OWNER_ID)

# --- 7. STARTUP ---
if __name__ == "__main__":
    print(f"✅ Starting PrivComBot on Python {PYTHON_VERSION}")
    keep_alive()  # Satisfies Render's port requirement
    print("🚀 Bot is online. Send /start in Telegram!")
    bot.run_until_disconnected()
