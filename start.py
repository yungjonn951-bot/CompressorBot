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

# --- 2. STAY-ALIVE SERVER (For Render) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run():
    # Render MUST see activity on this port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run, daemon=True).start()

# --- 3. BOT CONFIG ---
bot = TelegramClient('bot', int(os.getenv("API_ID")), os.getenv("API_HASH")).start(bot_token=os.getenv("BOT_TOKEN"))

# --- 4. THE COMPRESSION LOGIC ---
# We use a "Safe Import" so the bot doesn't crash if names are wrong
try:
    from helper.stuff import start as cmd_start, on_video
except ImportError:
    print("Warning: Could not import some functions from stuff.py")

@bot.on(events.NewMessage(pattern='/start'))
async def start_h(event):
    await cmd_start(event)

# THIS IS THE PART THAT COMPRESSES VIDEOS
@bot.on(events.NewMessage(incoming=True))
async def video_h(event):
    # If the message has a video or is a document/file
    if event.video or event.document:
        try:
            # This triggers the code in your helper/stuff.py
            await on_video(event, bot)
        except Exception as e:
            print(f"Compression error: {e}")

print("Bot is started. Send a video now!")
bot.run_until_disconnected()
