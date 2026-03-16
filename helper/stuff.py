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
import time
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import Button

# --- 1. DATABASE SETUP ---
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- 2. PROGRESS BAR & UTILS ---
def get_prog(current, total):
    percentage = (current / total) * 100
    completed = int(percentage / 10)
    return "█" * completed + "░" * (10 - completed), percentage

async def prog_cb(cur, tot, event, text):
    bar, per = get_prog(cur, tot)
    if int(per) % 10 == 0: # Update every 10% to prevent Telegram spam
        try:
            await event.edit(f"{text}\n\n{bar} **{per:.1f}%**")
        except: pass

def human_size(size_bytes):
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

import math # Needed for size calculation

# --- 3. CORE FUNCTIONS ---
async def add_user(u_id):
    try: await users_col.update_one({"user_id": u_id}, {"$set": {"user_id": u_id}}, upsert=True)
    except: pass

async def get_stats(event):
    count = await users_col.count_documents({})
    await event.reply(f"📊 **PrivComBot Stats**\n\nTotal Users: `{count}`")

async def start(event):
    await event.reply("Hi! I am **PrivComBot** 🤖\nSend a video to start!", buttons=[[Button.inline("📖 Help", data="help")]])

async def ihelp(event):
    await event.reply("**How to use:**\n1. Send a video.\n2. Select quality.\n3. Wait for the magic!")

async def broadcast(event, bot, owner):
    if event.sender_id != owner: return
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

# --- 4. THE COMPRESSION ENGINE ---
async def compress_video(event, bot, quality):
    crf_map = {"low": "30", "med": "24", "high": "20"}
    crf = crf_map.get(quality, "24")
    
    input_path = f"in_{event.id}.mp4"
    output_path = f"out_{event.id}.mp4"
    status = await event.edit("📥 **Downloading original file...**")
    
    try:
        # Get Original Size
        reply = await event.get_reply_message()
        orig_size = reply.video.size if reply.video else reply.document.size
        
        # 1. Download
        await bot.download_media(reply, input_path, progress_callback=lambda c, t: prog_cb(c, t, status, "📥 **Downloading...**"))
        
        # 2. Compression
        start_time = time.time()
        await status.edit(f"⚙️ **Processing {quality.upper()} Quality...**\n_This might take a while depending on size._")
        
        # Optimized FFmpeg command for Render
        cmd = ["ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", crf, "-preset", "ultrafast", "-acodec", "aac", "-y", output_path]
        
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()

        # 3. Final Comparison & Upload
        if os.path.exists(output_path):
            comp_size = os.path.getsize(output_path)
            saved_size = orig_size - comp_size
            saved_percent = (saved_size / orig_size) * 100
            time_taken = int(time.time() - start_time)

            await status.edit("📤 **Compression done! Uploading...**")
            
            caption = (
                f"✅ **Video Compressed!**\n\n"
                f"📁 **Original:** `{human_size(orig_size)}`\n"
                f"💎 **Compressed:** `{human_size(comp_size)}`\n"
                f"📉 **Saved:** `{human_size(saved_size)}` ({saved_percent:.1f}%)\n"
                f"⏱ **Time:** `{time_taken}s`"
            )

            await bot.send_file(
                event.chat_id, output_path, 
                caption=caption,
                progress_callback=lambda c, t: prog_cb(c, t, status, "📤 **Uploading...**")
            )
            await status.delete()
        else:
            await status.edit("❌ **Compression Failed!**\nThe file might be corrupted or too large for my server.")

    except Exception as e:
        await event.reply(f"❌ **Error:** `{str(e)}` \n_Try a smaller file._")
    
    finally:
        # Cleanup
        for p in [input_path, output_path]:
            if os.path.exists(p): os.remove(p)

