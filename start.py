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

# --- 1. SYSTEM SETUP ---
sys.path.append(os.getcwd())
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. ENVIRONMENT VARIABLES ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Extra variables from your Render settings
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
PORT = int(os.getenv("PORT", 8080))
PYTHON_VERSION = os.getenv("PYTHON_VERSION", "3.10") 

# --- 3. SAFETY CHECK ---
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("CRITICAL: Missing API_ID, API_HASH, or BOT_TOKEN!")
    sys.exit(1)

# --- 4. INITIALIZE CLIENT ---
# Simplified this line to avoid the 'datacenter' error
bot = TelegramClient('bot', int(API_ID), API_HASH).start(bot_token=BOT_TOKEN)

# Import handlers from helper/stuff.py
try:
    from helper.stuff import start, ihelp
except ImportError:
    from stuff import start, ihelp

# --- 5. HANDLERS ---
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if LOG_CHANNEL != 0:
        try:
            await bot.send_message(LOG_CHANNEL, f"👤 User `{event.sender_id}` started the bot.")
        except:
            pass
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

# --- 6. RUN ---
print(f"✅ Bot is ONLINE | Python: {PYTHON_VERSION} | Port: {PORT}")
bot.run_until_disconnected()


