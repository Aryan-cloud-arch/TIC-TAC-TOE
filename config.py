"""
CONFIGURATION - Environment variables and settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# MongoDB
MONGO_URL = os.getenv('MONGO_URL')

# Telegram Log Group
LOG_GROUP_ID = os.getenv('LOG_GROUP_ID')

# Admin IDs
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

# Forcesub (dynamic from database)
FORCESUB_ENABLED = False
FORCESUB_CHANNEL = None

# Game Settings
MOVE_TIMEOUT = 30  # seconds
CHALLENGE_TIMEOUT = 60  # seconds

# Points System
POINTS_WIN = 25
POINTS_LOSS = 5
POINTS_DRAW = 10

# Webhook (for Heroku)
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 8443))
