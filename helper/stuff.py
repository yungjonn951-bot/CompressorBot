#    This file is part of the CompressorBot distribution.
#    Copyright (c) 2021 yungjonn951-bot
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
#    License can be found in < https://github.com/yungjonn951-bot/CompressorBot/blob/main/License> .

import os
import asyncio
import math
import time
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import Button

# --- DATABASE SETUP ---
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- PROGRESS BAR LOGIC ---
def get_progress_bar(percentage):
    """Creates a visual progress bar [████░░░░░░]"""
    completed = int(percentage / 10)
    return "█" * completed + "░" * (10 - completed)

async def progress_callback(current, total, event, msg_text):
    """Updates the message with a progress bar during download/upload."""
    percentage = (current / total) * 100
    bar = get_progress_bar(percentage)
    
    # Only update every 5% to avoid Telegram rate limits (flood errors)
    if int(percentage) % 5 == 0:
        try:
            await event.edit(f"{msg_text}\n\n{bar} **{percentage:.1f}%**")
        except:
            pass

# --- USER HELPERS ---
async def add_user(user_id):
    try: await users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    except: pass

async def get_stats(event):
    count = await users_col.count_documents({})
    await event.reply(f"📊 **PrivComBot Stats**\n\nTotal Users: `{count}`")

# --- UI COMMANDS ---
async def start(event):
    await event.reply("Hi! I am **PrivComBot** 🤖\nSend a video to start!", buttons=[[Button.inline("📖 Help", data="help")]])

async def ihelp(event):
    await event.reply("**How to use:**\n1. Send a video.\n2. Select quality.\n3. Wait for the file!")

# --- COMPRESSION ENGINE ---
async def compress_video(event, bot, quality):
    crf_map = {"low": "30", "med": "24", "high": "20"}
    crf = crf_map.get(quality, "24")
    
    input_path = f"in_{event.id}.mp4"
    output_path = f"out_{event.id}.mp4"
    status = await event.edit("📥 **Starting Download...**")
    
    try:
        # 1. DOWNLOAD WITH PROGRESS
        reply = await event.get_reply_message()
        await bot.download_media(
            reply, input_path, 
            progress_callback=lambda c, t: progress_callback(c, t, status, "📥 **Downloading Video...**")
        )
        
        # 2. COMPRESSION
        await status.edit(f"⚙️ **Compressing to {quality.upper()}...**\n(This might take a minute)")
        cmd = ["ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", crf, "-preset", "ultrafast", "-acodec", "aac", "-y", output_path]
        
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()

        # 3. UPLOAD WITH PROGRESS
        if os.path.exists(output_path):
            await status.edit("📤 **Starting Upload...**")
            await bot.send_file(
                event.chat_id, output_path, 
                caption=f"✅ **Done!**\nQuality: {quality.upper()}",
                progress_callback=lambda c, t: progress_callback(c, t, status, "📤 **Uploading Result...**")
            )
            await status.delete()
        else:
            await status.edit("❌ Compression failed.")

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path): os.remove(path)
