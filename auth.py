#Copyright @ISmartCoder
#Updates Channel: https://t.me/TheSmartDev
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserIdInvalid, UsernameInvalid, PeerIdInvalid
from config import ADMIN_IDS, COMMAND_PREFIX
from core import authusers_collection
from utils import LOGGER
import asyncio
from datetime import datetime
import re

def sanitize(text):
    return re.sub(r'[^\w\s@.-]', '', text)

PAGE_SIZE = 5

def get_profile_link(user_id):
    return f"tg://user?id={user_id}"

@Client.on_message(filters.command("auth", prefixes=COMMAND_PREFIX) & filters.private)
async def auth_user(client, message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**")

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("**Please Provide A Username Or Userid To Auth ❌**")

    user_identifier = args[1].strip()
    try:
        user = await client.get_users(user_identifier)
        full_name = sanitize(f"{user.first_name or ''} {user.last_name or ''}").strip()
        username = user.username or "N/A"

        now = datetime.now()
        user_data = {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": username,
            "auth_time": now.strftime("%H:%M:%S"),
            "auth_date": now.strftime("%Y-%m-%d"),
            "auth_by_id": message.from_user.id,
            "auth_by_name": message.from_user.first_name
        }

        sent = await message.reply("**Authorizing User To Auth List✅**")
        await authusers_collection.update_one({"user_id": user.id}, {"$set": user_data}, upsert=True)
        await asyncio.sleep(1)
        await sent.edit(f"**Successfully Authorized User [{full_name}](tg://user?id={user.id}) ✅**")

    except (UserIdInvalid, UsernameInvalid, PeerIdInvalid, Exception) as e:
        LOGGER.error(f"Auth failed: {e}")
        await message.reply("** Sorry Failed To Authorize User ❌**")


@Client.on_message(filters.command("unauth", prefixes=COMMAND_PREFIX) & filters.private)
async def unauth_user(client, message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**")

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("**Please Provide A Username Or Userid To Unauth ❌**")

    user_identifier = args[1].strip()
    try:
        user = await client.get_users(user_identifier)
        full_name = sanitize(f"{user.first_name or ''} {user.last_name or ''}").strip()
        sent = await message.reply("**Demoting User To Auth List✅**")
        await authusers_collection.delete_one({"user_id": user.id})
        await asyncio.sleep(1)
        await sent.edit(f"**Successfully Demoted User [{full_name}](tg://user?id={user.id}) ✅**")

    except (UserIdInvalid, UsernameInvalid, PeerIdInvalid, Exception) as e:
        LOGGER.error(f"Unauth failed: {e}")
        await message.reply("** Sorry Failed To Unauthorize User ❌**")


@Client.on_message(filters.command("list", prefixes=COMMAND_PREFIX) & filters.private)
async def list_auth_users(client, message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**")

    page = 1
    await send_auth_list_page(client, message, page)


@Client.on_message(filters.text & filters.regex(r"💸 Auth Users") & filters.private)
async def list_auth_users_text(client, message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**")

    page = 1
    await send_auth_list_page(client, message, page)


async def send_auth_list_page(client, message, page):
    skip = (page - 1) * PAGE_SIZE
    users = await authusers_collection.find().skip(skip).limit(PAGE_SIZE).to_list(PAGE_SIZE)
    total_users = await authusers_collection.count_documents({})

    if not users:
        return await message.reply("**No Authorized Users Found ❌**")

    text = "**Twilio Authorized Users List Below ✅**\n**━━━━━━━━━━━━━━━━━━━━**\n"
    for user in users:
        full_name = sanitize(f"{user.get('first_name', '')} {user.get('last_name', '')}").strip()
        text += f"**⊗ Full Name:** **{full_name}**\n"
        text += f"**⊗ Username:** @{user.get('username', 'N/A')}\n"
        text += f"**⊗ UserID:**  `{user['user_id']}`\n"
        text += f"**⊗ Auth Time:** **{user.get('auth_time', 'N/A')}**\n"
        text += f"**⊗ Auth Date:** **{user.get('auth_date', 'N/A')}**\n"
        text += f"**⊗ Auth By:** [{user.get('auth_by_name')}](tg://user?id={user.get('auth_by_id')})\n"
        text += "**━━━━━━━━━━━━━━━━━━━━**\n"

    keyboard = []
    if page > 1:
        keyboard.append(InlineKeyboardButton("Previous", callback_data=f"auth_prev_{page - 1}"))
    if skip + PAGE_SIZE < total_users:
        keyboard.append(InlineKeyboardButton("Next", callback_data=f"auth_next_{page + 1}"))

    reply_markup = InlineKeyboardMarkup([keyboard]) if keyboard else None
    await message.reply(text, reply_markup=reply_markup, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r"auth_(prev|next)_(\d+)") & filters.user(ADMIN_IDS))
async def paginate_auth_users(client, callback_query):
    _, direction, page = callback_query.data.split("_")
    page = int(page)
    try:
        await callback_query.message.edit("Loading Page...")
        await send_auth_list_page(client, callback_query.message, page)
    except Exception as e:
        LOGGER.error(f"Pagination failed: {e}")
        await callback_query.answer("Error loading page", show_alert=True)