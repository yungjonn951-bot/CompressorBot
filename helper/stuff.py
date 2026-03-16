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
import time
import asyncio
import subprocess
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import Button

# --- DATABASE SETUP ---
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- USER HELPERS ---
async def add_user(user_id):
    try:
        await users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    except: pass

async def get_stats(event):
    count = await users_col.count_documents({})
    await event.reply(f"📊 **PrivComBot Stats**\n\nTotal Users: `{count}`")

# --- COMMANDS ---
async def start(event):
    await event.reply(
        "Hi! I am **PrivComBot** 🤖\nSend me a video to start compressing!",
        buttons=[[Button.inline("📖 Help", data="help")]]
    )

async def ihelp(event):
    await event.reply("Just send any video file, then choose the quality!")

# --- BROADCAST ---
async def broadcast(event, bot, OWNER_ID):
    if event.sender_id != OWNER_ID: return
    msg = await event.get_reply_message()
    if not msg: return await event.reply("Reply to a message!")
    status = await event.reply("🚀 Broadcasting...")
    sent = 0
    async for user in users_col.find():
        try:
            await bot.send_message(user["user_id"], msg)
            sent += 1
        except: pass
    await status.edit(f"✅ Sent to `{sent}` users.")

# --- COMPRESSION ENGINE ---
async def compress_video(event, bot, quality):
    # Mapping quality to CRF (Lower is better quality, higher is smaller size)
    crf_values = {"low": "30", "med": "24", "high": "20"}
    crf = crf_values.get(quality, "24")

    status = await event.edit("📥 **Downloading video...**")
    input_path = f"video_{event.chat_id}.mp4"
    output_path = f"compressed_{event.chat_id}.mp4"

    try:
        # Download the file
        original_msg = await event.get_reply_message()
        await bot.download_media(original_msg, input_path)
        
        await status.edit(f"⚙️ **Compressing to {quality.upper()}...**\nThis takes time, please wait.")
        
        # FFmpeg Command
        cmd = [
            "ffmpeg", "-i", input_path, 
            "-vcodec", "libx264", "-crf", crf, 
            "-preset", "veryfast", "-acodec", "aac", "-y", output_path
        ]
        
        # Run FFmpeg
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        await status.edit("📤 **Uploading compressed video...**")
        await bot.send_file(event.chat_id, output_path, caption=f"✅ Compressed to {quality.upper()} quality.")
        await status.delete()

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup files to save Render disk space
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
