#Copyright @ISmartCoder
#Updates Channel: https://t.me/TheSmartDev
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from pyrogram.enums import ParseMode
from core import authusers_collection
from config import ADMIN_IDS, COMMAND_PREFIX, DEVELOPER_ID, UPDATE_CHANNEL_URL


@Client.on_message(filters.command("start", prefixes=COMMAND_PREFIX) & filters.private)
async def start_handler(client, message):
    user = message.from_user
    user_id = user.id

    # Check if user is authorized (ADMIN or in DB)
    is_admin = user_id in ADMIN_IDS
    is_authorized = await authusers_collection.find_one({"user_id": user_id})

    if not is_admin and not is_authorized:
        return await client.send_message(
            chat_id=user_id,
            text="**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )

    fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()

    # Send welcome message with non-inline ReplyKeyboardMarkup
    await client.send_message(
        chat_id=user_id,
        text=(
            f"**Hi {fullname}! I Am TwilioSMSBot💸 The ultimate toolkit on Telegram, offering auto otp system, supreme features, lightning faster server otp.**\n\n"
            f"🛒 Choose An Option Below:"
        ),
        reply_markup=ReplyKeyboardMarkup(
            [
                ["🔐 Login", "🔍 Search Number"],
                ["👤 Account", "💸 Auth Users"],
                ["💰 Custom Area Code", "Get OTP💸"],
                ["Delete Number 🗑"]
            ],
            resize_keyboard=True
        ),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )