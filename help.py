#Copyright @ISmartCoder
#Updates Channel: https://t.me/TheSmartDev
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import ADMIN_IDS, COMMAND_PREFIX, DEVELOPER_ID, UPDATE_CHANNEL_URL
from core import authusers_collection
from utils import LOGGER

# Helper to check if user is authorized
async def is_authorized_user(user_id):
    if user_id in ADMIN_IDS:
        return True
    user = await authusers_collection.find_one({"user_id": user_id})
    return user is not None

# Filter for authorized users
def authorized_only():
    async def func(flt, client, message):
        return await is_authorized_user(message.from_user.id)
    return filters.create(func)

@Client.on_message(filters.command("help", prefixes=COMMAND_PREFIX) & filters.private & authorized_only())
async def help_command(client, message):
    help_text = (
        "<b>Showing Help Menu Of Smart Twilio:👇</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        "/start - Start Smart Twilio Bot\n"
        "/my - Get All Purchased Numbers\n"
        "/list - Get List Of All Auth Users\n"
        "/auth - Auth A User In DB\n"
        "/unauth - Remove A User From DB\n"
        "/del - Delete Purchased Numbers\n"
        "/get - Get OTP Manually From Server\n"
        "/login - Login To Twilio Account\n"
        "/logout - Logout From Twilio Account\n"
        "/info - Get User Info From Smart DB\n"
        "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Smart Twilio Bot By Smart Dev 🇧🇩</b>"
    )
    
    await message.reply(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Updates Channel", url=UPDATE_CHANNEL_URL)]
        ])
    )

@Client.on_message(filters.command("help", prefixes=COMMAND_PREFIX) & filters.private & ~authorized_only())
async def unauthorized_access(client, message):
    await message.reply(
        "<b>Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
        ])
    )