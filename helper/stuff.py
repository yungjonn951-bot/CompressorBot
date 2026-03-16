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
import math
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import Button

# --- DB SETUP ---
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- UTILS ---
def human_size(size_bytes):
    if size_bytes == 0: return "0B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    return f"{round(size_bytes / math.pow(1024, i), 2)} {('B', 'KB', 'MB', 'GB')[i]}"

async def add_user(u_id):
    try: await users_col.update_one({"user_id": u_id}, {"$set": {"user_id": u_id}}, upsert=True)
    except: pass

async def get_stats(event):
    count = await users_col.count_documents({})
    await event.reply(f"📊 **PrivComBot Stats**\nTotal Users: `{count}`")

# --- UI COMMANDS ---
async def start(event):
    await event.reply("🤖 **PrivComBot Pro**\nSend a video to compress!", buttons=[[Button.inline("📖 Help", data="help")]])

async def ihelp(event):
    text = (
        "🚀 **Compression Guide**\n\n"
        "📉 **Low Quality (30%)**: Maximum compression. Good for low data/fast sharing. Noticeable quality drop.\n\n"
        "📊 **Medium Quality (60%)**: The sweet spot. Great for mobile viewing with sharp enough detail.\n\n"
        "📈 **High Quality (80%)**: Premium feel. Visually identical to original but with a smaller file size."
    )
    await event.reply(text)

async def broadcast(event, bot, owner):
    if event.sender_id != owner: return
    msg = await event.get_reply_message()
    status = await event.reply("🚀 Broadcasting...")
    sent = 0
    async for user in users_col.find():
        try:
            await bot.send_message(user["user_id"], msg)
            sent += 1
        except: pass
    await status.edit(f"✅ Sent to `{sent}` users.")

# --- ENGINE ---
async def compress_video(event, bot, quality):
    crf_map = {"low": "30", "med": "24", "high": "20"}
    crf = crf_map.get(quality, "24")
    input_path, output_path = f"in_{event.id}.mp4", f"out_{event.id}.mp4"
    status = await event.edit("📥 **Downloading...**")
    
    try:
        reply = await event.get_reply_message()
        orig_size = reply.video.size if reply.video else reply.document.size
        await bot.download_media(reply, input_path)
        
        await status.edit(f"⚙️ **Processing {quality.upper()}...**")
        cmd = ["ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", crf, "-preset", "ultrafast", "-acodec", "aac", "-y", output_path]
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            comp_size = os.path.getsize(output_path)
            saved = ((orig_size - comp_size) / orig_size) * 100
            
            caption = (
                f"✅ **Success!**\n\n"
                f"📁 Original: `{human_size(orig_size)}`\n"
                f"💎 Compressed: `{human_size(comp_size)}`\n"
                f"📉 Saved: `{saved:.1f}%`"
            )
            
            # Post-compression rating buttons
            await bot.send_file(
                event.chat_id, output_path, caption=caption,
                buttons=[[Button.url("⭐ Rate Us", "https://t.me/your_bot_username_here")]]
            )
            await status.delete()
    except Exception as e:
        await event.reply(f"❌ Error: `{e}`")
    finally:
        for p in [input_path, output_path]:
            if os.path.exists(p): os.remove(p)

