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
import sys
from telethon import Button, events

# This line fixes the "No module named utils" error
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import GetFullUserRequest
except ImportError:
    # Backup if Render is being difficult
    from helper.utils import GetFullUserRequest

async def start(event):
    try:
        ok = await event.client(GetFullUserRequest(event.sender_id))
        first_name = ok.users[0].first_name
    except Exception:
        first_name = "User"

    await event.reply(
        f"Hi {first_name}! I am **PrivComBot** 🗜️",
        buttons=[[Button.inline("📖 Help", data="help")]]
    )

async def ihelp(event):
    await event.reply("Just send me a video file to begin!")

