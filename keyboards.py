from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_URL

def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Obuna bo'lish",
                    url=CHANNEL_URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data="participate"  # Keep callback same for backend
                )
            ]
        ]
    )

def stats_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Siz taklif qilganlar",
                    callback_data="my_stats"
                )
            ]
        ]
    )
