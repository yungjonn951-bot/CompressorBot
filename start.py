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
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- 1. SYSTEM SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 2. THE KEEP-ALIVE WEB SERVER (Fixes Render Port Error) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render uses the 'PORT' environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 3. CORE VARIABLES ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PYTHON_VERSION = os.getenv("PYTHON_VERSION", "3.10")

# --- 4. START THE BOT ---
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("Missing API_ID, API_HASH, or BOT_TOKEN!")
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
    print(f"✅ Bot is starting on Python {PYTHON_VERSION}")
    keep_alive() # Starts the fake website to satisfy Render
    print("🚀 Keep-alive server is running. Bot is ready!")
    bot.run_until_disconnected()


