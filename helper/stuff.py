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
# serverSelectionTimeoutMS=5000 tells the bot to give up after 5 seconds 
# instead of hanging forever if the connection is bad.
MONGO_URI = os.getenv("MONGO_URI")
db_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = db_client["PrivComBot"]
users_col = db["users"]

# --- 2. DATABASE HELPER ---
async def add_user(user_id):
    """Saves the user to MongoDB so they can receive broadcasts later."""
    try:
        await users_col.update_one(
            {"user_id": user_id}, 
            {"$set": {"user_id": user_id}}, 
            upsert=True
        )
    except Exception as e:
        print(f"❌ Database Error in add_user: {e}")

# --- 3. THE START COMMAND ---
async def start(event):
    """The /start command logic."""
    first_name = "User"
    try:
        # Fetching the user's name for a personalized welcome
        from helper.utils import GetFullUserRequest
        ok = await event.client(GetFullUserRequest(event.sender_id))
        first_name = ok.users[0].first_name
    except Exception:
        pass

    # Sending the welcome message with the Help button
    await event.reply(
        f"Hi {first_name}! I am **PrivComBot** 🤖\n\n"
        "I am a high-speed video compressor bot. Send me any video file, "
        "and I will reduce the size while keeping the quality high! 🚀",
        buttons=[[Button.inline("📖 Help", data="help")]]
    )

# --- 4. THE BROADCAST COMMAND ---
async def broadcast(event, bot, OWNER_ID):
    """Broadcasts a replied message to all users in the database."""
    if event.sender_id != OWNER_ID:
        return await event.reply("❌ This command is for the Owner only.")
    
    if not event.reply_to_msg_id:
        return await event.reply("Please **reply** to a message to broadcast it.")
    
    msg = await event.get_reply_message()
    status = await event.reply("🚀 Starting broadcast...")
    
    sent = 0
    total = 0
    
    try:
        async for user_doc in users_col.find():
            total += 1
            try:
                await bot.send_message(user_doc["user_id"], msg)
                sent += 1
            except Exception:
                # This happens if a user blocked the bot
                pass 
        
        await status.edit(f"✅ **Broadcast complete!**\n\n"
                          f"👤 Total Users: `{total}`\n"
                          f"📤 Sent: `{sent}`\n"
                          f"🚫 Failed/Blocked: `{total - sent}`")
    except Exception as e:
        await status.edit(f"❌ Broadcast failed: {e}")

# --- 5. THE HELP COMMAND ---
async def ihelp(event):
    """The /help command logic."""
    await event.reply(
        "**PrivComBot Help Menu**\n\n"
        "1️⃣ Send me any Video file.\n"
        "2️⃣ Choose your compression settings (Coming soon).\n"
        "3️⃣ Wait for the processed file!\n\n"
        "Queries? Contact the owner."
    )