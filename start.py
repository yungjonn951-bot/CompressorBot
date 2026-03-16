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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. REQUIRED CORE VARIABLES ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- 3. EXTRA VARIABLES (With Fallbacks) ---
# If these aren't in Render, the bot uses the second value provided
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
TG_DC = int(os.getenv("TG_DC", 1))
PORT = int(os.getenv("PORT", 8080))
PYTHON_VER = os.getenv("PYTHON_VERSION", "3.10")

# --- 4. SAFETY CHECK ---
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("CRITICAL: API_ID, API_HASH, or BOT_TOKEN missing in Render Environment!")
    sys.exit(1)

# --- 5. INITIALIZE CLIENT ---
# We use the TG_DC parameter here to tell the bot which data center to use
bot = TelegramClient('bot', int(API_ID), API_HASH, datacenter=TG_DC).start(bot_token=BOT_TOKEN)

# Import handlers from your helper folder
try:
    from helper.stuff import start, ihelp
except ImportError:
    from stuff import start, ihelp

# --- 6. HANDLERS ---
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # Optional: Log the start command to your Log Channel
    if LOG_CHANNEL != 0:
        await bot.send_message(LOG_CHANNEL, f"User {event.sender_id} started the bot.")
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

print(f"✅ Bot started on Port {PORT} using Python {PYTHON_VER}")
bot.run_until_disconnected()

