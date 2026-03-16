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
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events, Button

# --- SYSTEM SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)

app = Flask('')

@app.route('/')
def home():
    return "PrivComBot Pro is Live"

def run():
    # This grabs the PORT Render gives us, or uses 8080 as a backup
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # This starts the web server in a separate thread so the bot can run
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- START THE STAY-ALIVE SERVER ---
# This was the missing "Key" to turn on the engine
keep_alive()

# --- CONFIG ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Default to 0 if OWNER_ID is missing to prevent crash
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# --- BOT INITIALIZATION ---
bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

from helper.stuff import start, broadcast, add_user, get_stats

# --- THE ACTUAL BOT LOGIC ---
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await start(event)

# IMPORTANT: This keeps the bot listening to messages
print("Bot is successfully running...")
bot.run_until_disconnected()

