import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

from config import BOT_TOKEN, CHANNEL_USERNAME
from db import (
    init_db,
    add_user,
    set_participant,
    set_joined,
    get_referral_count,
    get_top_referrers,
    is_battle_active,
    set_battle,
    is_admin, ADMIN_IDS, reset_battle_data
)
from keyboards import start_keyboard, stats_keyboard

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
bot_username = None


# -------------------- Start Handler --------------------
@dp.message(CommandStart())
async def start(msg: types.Message, command: CommandStart):
    user_id = msg.from_user.id
    args = command.args

    referrer_id = None
    if args and args.startswith("ref_"):
        try:
            referrer_id = int(args.replace("ref_", ""))
            if referrer_id == user_id:
                referrer_id = None
        except ValueError:
            referrer_id = None

    username = msg.from_user.username
    await add_user(user_id, referrer_id, username)

    await ensure_joined_flag(user_id)

    await msg.answer(
        "🔥 Xush kelibsiz.\n\n"
        "1️⃣ Kanalga qo'shlish\n"
        "2️⃣ Yakunlash uchun — *Tasdiqlash* tugmasini bosing \n\n"
        "  ",
        reply_markup=start_keyboard(),
        parse_mode="Markdown",
    )


# -------------------- Helper Functions --------------------
async def ensure_joined_flag(user_id: int):
    if await has_joined_channel(user_id):
        await set_joined(user_id)


async def has_joined_channel(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        print("DEBUG get_chat_member:", user_id, member.status)
        return member.status in ("member", "administrator", "creator")
    except TelegramBadRequest as e:
        print("DEBUG TelegramBadRequest:", e)
        return False


# -------------------- Participate / Done --------------------
@dp.callback_query(lambda c: c.data == "participate")
async def participate(call: types.CallbackQuery):
    user_id = call.from_user.id

    if not await has_joined_channel(user_id):
        await call.message.answer(
            "❌ Birinchi kanalga obuna bo'ling\n\n"
            "Kanalga qo'shiling, va Tasdiqlash ni bosing!"
        )
        await call.answer()
        return

    await set_joined(user_id)
    await set_participant(user_id)

    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    await call.message.answer(
        "🚀 Muvoffaqqiyatli qo'shildingiz.\n\n"
        f"🔗 Do'stlaringizni taklif qiling!\nSizning referral:\n{referral_link}",
        reply_markup=stats_keyboard(),
    )
    await call.answer()


# -------------------- My Stats --------------------
@dp.callback_query(lambda c: c.data == "my_stats")
async def my_stats(call: types.CallbackQuery):
    user_id = call.from_user.id
    await ensure_joined_flag(user_id)

    count = await get_referral_count(user_id)
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    await call.message.answer(
        f"🔗 Do'stlaringizni taklif qiling!\nSizning referral:\n{referral_link}\n\n"
        f"👥 Taklif qilinganlar: {count}",
        reply_markup=stats_keyboard(),
    )
    await call.answer()


# -------------------- Admin Commands --------------------
@dp.message(lambda m: m.text and m.text.startswith("/"))
async def admin_commands(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    command = msg.text.lower()

    if command == "/start_battle":
        await set_battle(True)
        await msg.answer("⚡ O'yin boshlandi!")



    elif command == "/stop_battle":

        await set_battle(False)

        top = await get_top_referrers()

        if top:

            winner_text = "🏆 O'yin tugadi! Top o'yinchilar:\n"

            for idx, (ref_id, cnt, username) in enumerate(top, 1):

                name = f"@{username}" if username else f"ID:{ref_id}"

                winner_text += f"{idx}. {name} — {cnt} bal\n"

                try:

                    await bot.send_message(

                        ref_id,

                        f"🎉 Tabriklaymiz!\n"

                        f"Siz #{idx}-o'rinni oldingiz ({cnt} bal).\n"

                        f"Yutuq uchun adminga screenshot yuboring: @Realfoundr"

                    )

                except:

                    pass

            for admin_id in ADMIN_IDS:
                await bot.send_message(admin_id, winner_text)

        await msg.answer("🛑 O'yin yakunlandi va g'oliblarga xabar yuborildi!")




    elif command == "/top_referrers":

        top = await get_top_referrers(10)

        if not top:
            await msg.answer("No referrers yet.")

            return

        text = "🏆 Top referrers:\n"

        for idx, (ref_id, cnt, username) in enumerate(top, 1):
            name = f"@{username}" if username else f"ID:{ref_id}"
            text += f"{idx}. {name} → {cnt}\n"

        await msg.answer(text)


    elif command == "/status":
        active = await is_battle_active()
        await msg.answer(f"⚡ Battle is {'active' if active else 'inactive'}")


# -------------------- Main --------------------
async def main():
    global bot_username
    await init_db()
    me = await bot.get_me()
    bot_username = me.username
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
