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
from telethon import TelegramClient, events, Button

# --- 1. THE STAY-ALIVE SERVER (Render Health Check) ---
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

# --- 3. IMPORT COMPRESSOR LOGIC ---
import helper.stuff as stuff
available_funcs = dir(stuff)

# --- 4. THE HANDLERS ---

# Handle /start
@bot.on(events.NewMessage(pattern='/start'))
async def start_h(event):
    if 'start' in available_funcs:
        await stuff.start(event)
    else:
        await event.reply("Bot is online! Send a video to begin.")

# Handle Video Sensing (Triggers the menu)
@bot.on(events.NewMessage)
async def video_h(event):
    if event.video or (event.document and "video" in (event.document.mime_type or "")):
        # Most bots use on_video to show the buttons
        if 'on_video' in available_funcs:
            await stuff.on_video(event, bot)

# --- 5. THE BUTTON CLICK FIX (Callback Handler) ---
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    # This turns b'low' into 'low'
    quality_choice = event.data.decode('utf-8')
    
    # Answer the click so the loading icon disappears
    await event.answer(f"Selected: {quality_choice}")

    try:
        if 'compress_video' in available_funcs:
            # We get the original message that had the video
            msg = await event.get_message()
            
            # WE PASS THE QUALITY HERE - This fixes your 'missing argument' error
            await stuff.compress_video(msg, bot, quality=quality_choice)
        else:
            await event.edit(f"Function 'compress_video' not found in stuff.py")
    except Exception as e:
        await event.reply(f"Button Error: {e}")

print("Bot is LIVE. Listening for videos and button clicks...")
bot.run_until_disconnected()

