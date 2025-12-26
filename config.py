import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Use ID instead of username
CHANNEL_URL = os.getenv("CHANNEL_URL")  # Keep the invite link if needed
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")  # Keep the invite link if needed
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
if not ADMIN_IDS:
    ADMIN_IDS = []
else:
    # Convert comma-separated string to list of ints
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS.split(",")]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not CHANNEL_ID:
    raise RuntimeError("CHANNEL_ID is not set")

if not CHANNEL_URL:
    raise RuntimeError("CHANNEL_URL is not set")
