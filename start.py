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
from telethon import TelegramClient, events, Button

# --- SYSTEM SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)
app = Flask('')

@app.route('/')
def home(): return "PrivComBot Pro is Live"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))))
    t.daemon = True
    t.start()

# --- CONFIG ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)
from helper.stuff import start, ihelp, broadcast, add_user, get_stats, compress_video

# --- QUEUE SYSTEM ---
video_queue = []
is_processing = False

async def process_queue():
    global is_processing
    if is_processing or not video_queue: return
    is_processing = True
    event, quality = video_queue.pop(0)
    try:
        await compress_video(event, bot, quality)
    except Exception as e:
        logging.error(f"Queue Error: {e}")
    is_processing = False
    await process_queue()

# --- HANDLERS ---
@bot.on(events.NewMessage(pattern='/start'))
async def h_start(e):
    await add_user(e.sender_id)
    await start(e)

@bot.on(events.NewMessage(pattern='/help'))
async def h_help(e):
    await ihelp(e)

@bot.on(events.NewMessage(pattern='/stats'))
async def h_stats(e):
    await get_stats(e)

@bot.on(events.NewMessage(pattern='/broadcast'))
async def h_brd(e):
    await broadcast(e, bot, OWNER_ID)

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.video or e.document))
async def video_handler(event):
    obj = event.video or event.document
    if event.document and not obj.mime_type.startswith('video/'): return 
    
    size_mb = obj.size / (1024 * 1024)
    await event.reply(
        f"📂 **File Detected!**\n📏 Original Size: `{size_mb:.2f} MB`\n\n"
        "Select Quality (tap /help for details):",
        buttons=[
            [Button.inline("📉 Low (30%)", data="qual_low"), Button.inline("📊 Med (60%)", data="qual_med")],
            [Button.inline("📈 High (80%)", data="qual_high")]
        ]
    )

@bot.on(events.CallbackQuery(pattern=r"qual_"))
async def quality_callback(event):
    quality = event.data.decode('utf-8').split('_')[1]
    video_queue.append((event, quality))
    if is_processing:
        await event.edit(f"⏳ **In Queue...** Position: `{len(video_queue)}`")
    else:
        await event.edit(f"🚀 **Initializing {quality.upper()} compression...**")
    await process_queue()

if __name__ == "__main__":
    keep_alive()
    bot.run_until_disconnected()

