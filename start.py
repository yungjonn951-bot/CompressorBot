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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- STAY ALIVE (FLASK) SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "PrivComBot Pro is Live and Healthy"

def run():
    # Render assigns a port dynamically; this ensures we catch it.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Start the web server immediately
keep_alive()

# --- CONFIG ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# --- BOT INITIALIZATION ---
bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

# Import the logic from your helper file
# Note: Ensure these function names match exactly what is inside helper/stuff.py
from helper.stuff import start, help, on_video

# --- BOT HANDLERS ---

# 1. Handle /start command
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await start(event)

# 2. Handle /help command
@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    # If your helper file has a specific 'help' function
    try:
        await help(event)
    except Exception as e:
        logger.error(f"Help error: {e}")
        await event.reply("Use /start to see available options.")

# 3. Handle Video Files (The Compression Trigger)
@bot.on(events.NewMessage(incoming=True, func=lambda e: e.video or e.document))
async def video_handler(event):
    # This sends the video to the compression logic in stuff.py
    try:
        await on_video(event, bot)
    except Exception as e:
        logger.error(f"Compression error: {e}")

# 4. Global Error Handler to prevent the bot from dying
@bot.on(events.NewMessage)
async def all_messages(event):
    # This just ensures the bot stays active for any text
    pass

# --- START THE ENGINE ---
print("------------------------------")
print("PrivComBot Pro is now Online!")
print("------------------------------")

bot.run_until_disconnected()
