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

# --- 1. THE STAY-ALIVE SERVER ---
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

# --- 3. SMART IMPORT & FUNCTION SCANNER ---
import helper.stuff as stuff
available_funcs = dir(stuff)

# --- 4. THE HANDLERS ---

# Handle /start - This sends the menu buttons
@bot.on(events.NewMessage(pattern='/start'))
async def start_h(event):
    if 'start' in available_funcs:
        await stuff.start(event)
    else:
        # Fallback if your helper doesn't have a start function
        await event.reply("Welcome! Send me a video and then choose the quality.")

# Handle VIDEO SENSING
@bot.on(events.NewMessage)
async def video_h(event):
    if event.video or event.document:
        # Many bots send a button menu AS SOON as a video is received
        # If your bot doesn't do that, it will try to compress immediately
        try:
            if 'compress_video' in available_funcs:
                # We try to run it with a default, but if it fails, 
                # the buttons below will handle the specific choice.
                await stuff.compress_video(event, bot, quality="medium")
        except Exception as e:
            print(f"Waiting for button click or auto-compress error: {e}")

# --- 5. THE BUTTON CLICK IMPROVEMENT ---
# This is the "secret sauce" for the menu buttons
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    # 'data' is what the button sends back (e.g., b'low', b'medium')
    choice = event.data.decode('utf-8')
    
    # We must answer the callback so the "loading" circle stops on Telegram
    await event.answer(f"Quality selected: {choice}")
    
    try:
        # This calls your compression function with the button you clicked!
        if 'compress_video' in available_funcs:
            # We fetch the original video message the buttons were attached to
            msg = await event.get_message()
            await stuff.compress_video(msg, bot, quality=choice)
        else:
            await event.edit(f"Function 'compress_video' not found. Available: {available_funcs}")
    except Exception as e:
        await event.edit(f"Button Error: {e}")

print("Bot is LIVE. Listening for videos and button clicks.")
bot.run_until_disconnected()
