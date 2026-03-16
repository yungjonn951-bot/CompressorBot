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
from telethon import Button,
events
import sys
import os
sys.path.append(os.getcwd())

# This ensures the bot finds the 'helper' folder correctly
sys.path.append(os.getcwd())

# This handles both ways the bot might try to load the file
try:
    from utils import GetFullUserRequest
except ImportError:
    from helper.utils import GetFullUserRequest

# --- START COMMAND ---
async def start(event):
    try:
        ok = await event.client(GetFullUserRequest(event.sender_id))
        first_name = ok.users[0].first_name
    except:
        first_name = "User"

    await event.reply(
        f"Hi `{first_name}`! **I am PrivComBot** 🗜️\n\n"
        "I can compress your videos to save data while maintaining quality.\n\n"
        "**How to use:** Just send me a video file!",
        buttons=[
            [
                Button.inline("⚙️ Settings", data="settings"),
                Button.inline("📖 Help", data="help")
            ],
            [
                Button.url("👨‍💻 Developer", "https://t.me/YUNG_JONN_007"),
                Button.url("🛡️ Privacy Policy", "https://telegra.ph/PrivComBot-Privacy-Policy")
            ]
        ]
    )

# --- HELP COMMAND ---
async def ihelp(event):
    await event.reply(
        "**PrivComBot Help Menu** 📖\n\n"
        "1. **Compress:** Send any video file.\n"
        "2. **Settings:** Change output quality.\n"
        "Need more help? Contact the developer below.",
        buttons=[
            [Button.url("💬 Support", "https://t.me/YUNG_JONN_007")],
            [Button.inline("⬅️ Back", data="start_back")]
        ]
    )

# --- BUTTON BRAIN (CALLBACKS) ---
@bot.on(events.CallbackQuery)
async def callback(event):
    if event.data == b'settings':
        await event.answer("Settings coming soon!", alert=True)
    elif event.data == b'help':
        await event.answer()
        await ihelp(event)
    elif event.data == b'start_back':
        await event.answer()
        await start(event)
