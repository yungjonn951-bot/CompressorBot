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
import asyncio
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events

# --- 1. SYSTEM & LOGGING SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 2. RENDER KEEP-ALIVE (FLASK) ---
app = Flask('')
@app.route('/')
def home(): return "PrivComBot is Running!"

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

# --- 4. INITIALIZE CLIENT ---
bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

# Import logic from helper/stuff.py
from helper.stuff import start, ihelp, broadcast, add_user

# --- 5. COMMAND HANDLERS ---

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # This block prevents the bot from staying silent if MongoDB fails
    try:
        # Try to save user with a 5-second timeout
        await asyncio.wait_for(add_user(event.sender_id), timeout=5.0)
    except Exception as e:
        logger.error(f"MongoDB Error: {e}")
        print("⚠️ Database connection failed, but continuing to reply...")

    # The bot will now always reply even if the database is down
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

@bot.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_handler(event):
    await broadcast(event, bot, OWNER_ID)

# --- 6. STARTUP ---
if __name__ == "__main__":
    print("✅ PrivComBot is booting...")
    keep_alive()
    print("🚀 Bot is online. Testing response now!")
    bot.run_until_disconnected()
