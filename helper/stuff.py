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
import subprocess
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import Button

# --- 1. DATABASE SETUP ---
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- 2. USER HELPERS ---
async def add_user(user_id):
    """Saves user ID to MongoDB."""
    try:
        await users_col.update_one(
            {"user_id": user_id}, 
            {"$set": {"user_id": user_id}}, 
            upsert=True
        )
    except Exception as e:
        print(f"❌ DB Error: {e}")

async def get_stats(event):
    """Returns total user count."""
    count = await users_col.count_documents({})
    await event.reply(f"📊 **PrivComBot Stats**\n\nTotal Users: `{count}`")

# --- 3. UI COMMANDS ---
async def start(event):
    await event.reply(
        "Hi! I am **PrivComBot** 🤖\n\nSend me a video file to begin compression!",
        buttons=[[Button.inline("📖 Help", data="help")]]
    )

async def ihelp(event):
    await event.reply(
        "**How to use:**\n1. Send a video.\n2. Select quality.\n3. Wait for the link!"
    )

# --- 4. BROADCAST ---
async def broadcast(event, bot, OWNER_ID):
    if event.sender_id != OWNER_ID:
        return await event.reply("❌ Owner only.")
    msg = await event.get_reply_message()
    if not msg:
        return await event.reply("Reply to a message to broadcast.")
    
    status = await event.reply("🚀 Broadcasting...")
    sent = 0
    async for user in users_col.find():
        try:
            await bot.send_message(user["user_id"], msg)
            sent += 1
        except: pass
    await status.edit(f"✅ Sent to `{sent}` users.")

# --- 5. COMPRESSION ENGINE ---
async def compress_video(event, bot, quality):
    """Downloads, compresses via FFmpeg, and uploads."""
    # CRF: 18-28 is standard. Higher = smaller file/lower quality.
    crf_map = {"low": "30", "med": "24", "high": "20"}
    crf = crf_map.get(quality, "24")

    # Use unique filenames based on event ID to avoid conflicts
    input_path = f"in_{event.id}.mp4"
    output_path = f"out_{event.id}.mp4"

    status = await event.edit("📥 **Downloading...**")
    
    try:
        # Get the original video message
        reply = await event.get_reply_message()
        await bot.download_media(reply, input_path)
        
        await status.edit(f"⚙️ **Compressing ({quality.upper()})...**\nThis uses heavy CPU, please wait.")

        # FFmpeg command optimized for Render (ultrafast)
        cmd = [
            "ffmpeg", "-i", input_path,
            "-vcodec", "libx264", "-crf", crf,
            "-preset", "ultrafast", 
            "-acodec", "aac", "-y", output_path
        ]

        # Run process and wait
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        if not os.path.exists(output_path):
            return await status.edit("❌ Compression failed. Check logs.")

        await status.edit("📤 **Uploading...**")
        await bot.send_file(
            event.chat_id, 
            output_path, 
            caption=f"✅ **Done!**\nQuality: {quality.upper()}"
        )
        await status.delete()

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup to prevent Render disk full errors
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
