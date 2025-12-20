import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_URL = os.getenv("CHANNEL_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not CHANNEL_USERNAME:
    raise RuntimeError("CHANNEL_USERNAME is not set")

if not CHANNEL_URL:
    raise RuntimeError("CHANNEL_URL is not set")
