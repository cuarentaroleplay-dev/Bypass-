#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import ADMIN_IDS, COMMAND_PREFIX, DEVELOPER_ID
from core import authusers_collection, logindb_collection
from utils import LOGGER
import aiohttp
import base64
from datetime import datetime

async def is_authorized_user(user_id):
    if user_id in ADMIN_IDS:
        return True
    user = await authusers_collection.find_one({"user_id": user_id})
    return user is not None

def authorized_only():
    async def func(flt, client, message):
        return await is_authorized_user(message.from_user.id)
    return filters.create(func)

async def is_logged_in(user_id):
    user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
    return user_data is not None

def get_auth_header(sid, auth_token):
    auth_str = f"{sid}:{auth_token}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    return f"Basic {auth_b64}"

@Client.on_message((filters.command("get", prefixes=COMMAND_PREFIX) | filters.regex(r"^Get OTP💸$")) & filters.private & authorized_only())
async def get_command(client, message):
    user_id = message.from_user.id

    if not await is_logged_in(user_id):
        await message.reply(
            "<b>Sorry, Please First Login Using /login ❌</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Developer", user_id=DEVELOPER_ID)]
            ])
        )
        return

    loading_message = await message.reply(
        "<b>Getting All Latest OTP Messages</b>",
        parse_mode=ParseMode.HTML
    )

    user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
    if not user_data:
        await loading_message.edit(
            "<b>Please First Login Using /login</b>",
            parse_mode=ParseMode.HTML
        )
        return

    sid = user_data["sid"]
    auth_token = user_data["auth_token"]

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json?PageSize=10"
    headers = {"Authorization": get_auth_header(sid, auth_token)}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                response_text = await resp.text()
                LOGGER.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Fetch OTP messages API response for user_id {user_id}: Status {resp.status}, Response {response_text}")
                if resp.status != 200:
                    error_message = f"** Failed to fetch messages.**\nDetails: HTTP {resp.status}"
                    try:
                        error_data = await resp.json()
                        error_message += f" - {error_data.get('message', 'Unknown error')}"
                    except ValueError:
                        error_message += f" - {response_text}"
                    await loading_message.edit(error_message, parse_mode=ParseMode.MARKDOWN)
                    return

                data = await resp.json()
                messages = data.get("messages", [])
                if not messages:
                    await loading_message.edit(
                        "**Sorry No messages found**",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return

                text = "**Latest OTP Messages:**\n\n"
                for msg in messages:
                    if msg.get("direction") == "inbound":
                        text += f"{msg.get('from')} -> {msg.get('body')}\n"

                await loading_message.edit(
                    text or "**Sorry No OTPs found**",
                    parse_mode=ParseMode.MARKDOWN
                )
        except aiohttp.ClientError as e:
            LOGGER.error(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Network error during get_otp for user_id {user_id}: {str(e)}")
            await loading_message.edit(
                "** Network error while fetching OTPs. Please try again.**",
                parse_mode=ParseMode.MARKDOWN
            )

@Client.on_message((filters.command("get", prefixes=COMMAND_PREFIX) | filters.regex(r"^Get OTP💸$")) & filters.private & ~authorized_only())
async def unauthorized_access(client, message):
    await message.reply(
        "<b>Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
        ])
    )