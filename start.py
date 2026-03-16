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

# --- 1. SETUP ---
logging.basicConfig(level=logging.INFO)
sys.path.append(os.getcwd())

# --- 2. STAY-ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run, daemon=True).start()

# --- 3. BOT INITIALIZATION ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Import the compressor logic
try:
    from helper.stuff import start as cmd_start, on_video
    print("Successfully imported compression logic!")
except Exception as e:
    print(f"IMPORT ERROR: {e}")

# --- 4. THE HANDLERS ---

# Handle /start
@bot.on(events.NewMessage(pattern='/start'))
async def start_h(event):
    await cmd_start(event)

# THE AGGRESSIVE VIDEO SCANNER (Works for forwarded videos too)
@bot.on(events.NewMessage)
async def global_handler(event):
    # Log everything to Render so you can see the bot is working
    print(f"Message received! Video: {bool(event.video)}, Doc: {bool(event.document)}")

    # If it's a video OR a document that looks like a video
    is_video = event.video or (event.document and event.document.mime_type and "video" in event.document.mime_type)
    
    if is_video:
        print("Video detected! Sending to compressor...")
        try:
            await on_video(event, bot)
        except Exception as e:
            print(f"COMPRESSION CRASH: {e}")
            await event.reply(f"Error starting compression: {e}")

print("Bot is fully active. SEND A VIDEO NOW.")
bot.run_until_disconnected()
