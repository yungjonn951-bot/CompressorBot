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

import os, sys, logging
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# --- 1. THE STAY-ALIVE (DO NOT TOUCH) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
Thread(target=run, daemon=True).start()

# --- 2. BOT LOGIN ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- 3. THE "SMART" IMPORT ---
# This part checks what your helper file is actually named
import helper.stuff as stuff
available_functions = dir(stuff)
print(f"DEBUG: Functions found in stuff.py: {available_functions}")

# --- 4. THE HANDLERS ---

@bot.on(events.NewMessage(pattern='/start'))
async def start_h(event):
    if 'start' in available_functions:
        await stuff.start(event)
    else:
        await event.reply("Bot is online! Send a video to test.")

@bot.on(events.NewMessage)
async def video_h(event):
    if event.video or event.document:
        # We try the three most common names for compressor bots
        try:
            if 'on_video' in available_functions:
                await stuff.on_video(event, bot)
            elif 'compress_video' in available_functions:
                await stuff.compress_video(event, bot)
            elif 'video_handler' in available_functions:
                await stuff.video_handler(event, bot)
            else:
                await event.reply(f"Error: I found these functions {available_functions} but none match 'on_video'.")
        except Exception as e:
            await event.reply(f"Compression error: {e}")

print("Bot is LIVE. Send a video.")
bot.run_until_disconnected()
