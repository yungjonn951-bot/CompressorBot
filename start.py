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
from telethon import TelegramClient,events

# 1. Path Setup
sys.path.append(os.getcwd())

# 2. Logging (So you can see errors in Render logs)
logging.basicConfig(level=logging.INFO)

# 3. Import functions from helper
from helper.stuff import start, ihelp

# 4. Credentials (Ensure these are set in Render Environment Variables)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# 5. DEFINE THE BOT FIRST (Fixes the NameError)
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 6. NOW ADD THE HANDLERS
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await start(event)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await ihelp(event)

# Optional: Add CallbackQuery handler if you have buttons
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    if event.data == b'help':
        await ihelp(event)

print("SUCCESS: Bot is running...")
bot.run_until_disconnected()
