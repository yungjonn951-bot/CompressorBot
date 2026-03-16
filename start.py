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

# --- 1. LOGGING & SYSTEM ---
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 2. RENDER KEEP-ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "PrivComBot Professional is Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 3. CONFIGURATION ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

# Importing the logic from our Pro stuff.py
from helper.stuff import start, ihelp, broadcast, add_user, get_stats, compress_video

# --- 4. THE QUEUE SYSTEM ---
# This prevents your Render server from crashing (512MB RAM limit)
video_queue = []
is_processing = False

async def process_queue():
    global is_processing
    if is_processing or not video_queue:
        return
    
    is_processing = True
    # Get the next video task
    event, quality = video_queue.pop(0)
    
    try:
        await compress_video(event, bot, quality)
    except Exception as e:
        logger.error(f"Queue Error: {e}")
    
    is_processing = False
    # Check if there are more videos waiting
    await process_queue()

# --- 5. COMMAND HANDLERS ---

@bot.on(events.NewMessage(pattern='/start'))
async def h_start(e):
    await add_user(e.sender_id)
    await start(e)

@bot.on(events.NewMessage(pattern='/stats'))
async def h_stats(e):
    await get_stats(e)

@bot.on(events.NewMessage(pattern='/broadcast'))
async def h_broadcast(e):
    await broadcast(e, bot, OWNER_ID)

# --- 6. PROFESSIONAL VIDEO HANDLER ---

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.video or e.document))
async def video_handler(event):
    # Filter for videos only
    obj = event.video or event.document
    if event.document and not obj.mime_type.startswith('video/'):
        return 

    # Calculate file size for the user
    size_mb = obj.size / (1024 * 1024)
    
    # Professional Preview Message
    await event.reply(
        f"📂 **File Detected!**\n\n"
        f"📏 **Original Size:** `{size_mb:.2f} MB`\n"
        f"🛠 **Action:** Choose compression quality below.\n\n"
        f"ℹ️ _Your file will be added to the queue._",
        buttons=[
            [Button.inline("📉 Low (30%)", data="qual_low"), Button.inline("📊 Med (60%)", data="qual_med")],
            [Button.inline("📈 High (80%)", data="qual_high")]
        ]
    )

@bot.on(events.CallbackQuery(pattern=r"qual_"))
async def quality_callback(event):
    quality = event.data.decode('utf-8').split('_')[1]
    
    # Add task to queue
    video_queue.append((event, quality))
    
    # Inform user of their position
    pos = len(video_queue)
    if is_processing:
        await event.edit(f"⏳ **Added to Queue!**\nPosition: `{pos}`\n\nPlease wait, I am processing another video.")
    else:
        await event.edit(f"🚀 **Starting!**\nYou are first in line. Initializing {quality.upper()} compression...")
    
    # Trigger the queue processing
    await process_queue()

# --- 7. MAIN BOOT ---
if __name__ == "__main__":
    print("✅ PrivComBot Pro Initialized.")
    keep_alive()
    bot.run_until_disconnected()


