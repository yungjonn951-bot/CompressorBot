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
from telethon import TelegramClient, events

# Add current path to system
sys.path.append(os.getcwd())

# Setup logging
logging.basicConfig(level=logging.INFO)

# Import from helper folder
try:
    from helper.stuff import start, ihelp
except ImportError:
    from stuff import start, ihelp

# Replace the old credential section with this:
try:
    API_ID = int(os.environ.get("API_ID").strip())
    API_HASH = os.environ.get("API_HASH").strip()
    BOT_TOKEN = os.environ.get("BOT_TOKEN").strip()
except Exception as e:
    print(f"CRITICAL ERROR: Could not read Environment Variables. Check Render Settings! Details: {e}")
    sys.exit(1)

# Define bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

print("Bot is running...")
bot.run_until_disconnected()
