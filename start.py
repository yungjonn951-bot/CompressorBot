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
from telethon import TelegramClient, events

# --- SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Start the keep-alive server immediately
keep_alive()

# --- CONFIG ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

# IMPORT ALL FUNCTIONS FROM STUFF.PY
# We use 'try/except' so if one function is missing, the bot doesn't crash
try:
    from helper.stuff import start as start_func, help as help_func, on_video
except ImportError as e:
    logger.error(f"Could not import helper functions: {e}")

# --- HANDLERS ---

@bot.on(events.NewMessage(pattern='/start'))
async def handler_start(event):
    await start_func(event)

@bot.on(events.NewMessage(pattern='/help'))
async def handler_help(event):
    await help_func(event)

# THIS IS THE COMPRESSION TRIGGER
@bot.on(events.NewMessage(incoming=True, func=lambda e: e.video or e.document))
async def handler_video(event):
    # Only try to compress if it's a video file
    if event.video or (event.document and event.document.mime_type.startswith('video/')):
        await on_video(event, bot)

print("Bot is fully online. Send a video to test.")
bot.run_until_disconnected()
