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

# --- 1. SETUP PATHS & LOGGING ---
sys.path.append(os.getcwd())
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. SECURE CREDENTIAL CHECK ---
# We use os.getenv() so it doesn't crash if the variable is missing
API_ID_ENV = os.getenv("API_ID")
API_HASH_ENV = os.getenv("API_HASH")
BOT_TOKEN_ENV = os.getenv("BOT_TOKEN")

# Check if any variables are missing before trying to use them
if not all([API_ID_ENV, API_HASH_ENV, BOT_TOKEN_ENV]):
    logger.error("!!! CONFIGURATION ERROR !!!")
    if not API_ID_ENV: logger.error("- API_ID is missing in Render Environment tab")
    if not API_HASH_ENV: logger.error("- API_HASH is missing in Render Environment tab")
    if not BOT_TOKEN_ENV: logger.error("- BOT_TOKEN is missing in Render Environment tab")
    sys.exit(1)

# Safely convert API_ID to integer
try:
    API_ID = int(API_ID_ENV.strip())
    API_HASH = API_HASH_ENV.strip()
    BOT_TOKEN = BOT_TOKEN_ENV.strip()
except ValueError:
    logger.error("API_ID must be a number! Check your Render settings.")
    sys.exit(1)

# --- 3. IMPORT HANDLERS ---
try:
    from helper.stuff import start, ihelp
except ImportError as e:
    logger.error(f"Could not find helper files: {e}")
    sys.exit(1)

# --- 4. START THE BOT ---
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

print("✅ Bot is online and waiting for messages!")
bot.run_until_disconnected()

