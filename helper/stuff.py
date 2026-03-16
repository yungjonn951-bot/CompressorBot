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
from motor.motor_asyncio import AsyncIOMotorClient
from telethon import Button

# --- 1. DATABASE SETUP ---
# Make sure you added MONGO_URI to Render Environment Variables!
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- 2. DATABASE HELPER ---
async def add_user(user_id):
    await users_col.update_one(
        {"user_id": user_id}, 
        {"$set": {"user_id": user_id}}, 
        upsert=True
    )

# --- 3. THE START COMMAND ---
async def start(event):
    # Save the user to MongoDB first
    await add_user(event.sender_id)
    
    first_name = "User"
    try:
        # Your existing logic to get the name
        from helper.utils import GetFullUserRequest
        ok = await event.client(GetFullUserRequest(event.sender_id))
        first_name = ok.users[0].first_name
    except:
        pass

    await event.reply(
        f"Hi {first_name}! I am **PrivComBot** 🤖",
        buttons=[[Button.inline("📖 Help", data="help")]]
    )

# --- 4. THE BROADCAST COMMAND ---
async def broadcast(event, bot, OWNER_ID):
    if event.sender_id != OWNER_ID:
        return await event.reply("❌ This command is for the Owner only.")
    
    if not event.reply_to_msg_id:
        return await event.reply("Please **reply** to a message to broadcast it.")
    
    msg = await event.get_reply_message()
    status = await event.reply("🚀 Starting broadcast...")
    
    sent = 0
    async for user_doc in users_col.find():
        try:
            await bot.send_message(user_doc["user_id"], msg)
            sent += 1
        except:
            pass # User might have blocked the bot

    await status.edit(f"✅ Broadcast complete!\nSent to: `{sent}` users.")

# --- 5. THE HELP COMMAND ---
async def ihelp(event):
    await event.reply("Just send me a video file to begin!")
