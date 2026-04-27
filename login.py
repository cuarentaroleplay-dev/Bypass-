#Copyright @ISmartCoder
#Updates Channel: https://t.me/TheSmartDev
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import ADMIN_IDS, COMMAND_PREFIX, DEVELOPER_ID
from core import authusers_collection, logindb_collection
from utils import LOGGER
import asyncio
import re
from twilio.rest import Client as TwilioClient

def clean_text(text):
    return re.sub(r"[^\w\s@.-]", "", text or "")

# Store conversation state for each user
user_states = {}

async def is_authorized(user_id):
    if user_id in ADMIN_IDS:
        return True
    return await authusers_collection.find_one({"user_id": user_id}) is not None

@Client.on_message(filters.command(["login"], prefixes=COMMAND_PREFIX) & filters.private)
async def login_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_authorized(user_id):
        return await message.reply(
            "**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
            ])
        )

    # Split command arguments
    args = message.text.split(maxsplit=2)[1:]  # Get arguments after /login
    if len(args) != 2:
        return await message.reply(
            "**Usage: /login {SID} {Auth Token} ❌**",
            parse_mode=ParseMode.MARKDOWN
        )

    sid, auth_token = args
    sent = await message.reply(
        "**Logging To Twilio Account...**",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        # Check if user is already logged in and log them out
        existing_user = await logindb_collection.find_one({"user_id": user_id})
        if existing_user and existing_user.get("logged_in", False):
            await logindb_collection.update_one(
                {"user_id": user_id},
                {"$set": {"logged_in": False}}
            )
            LOGGER.info(f"User {user_id} automatically logged out from previous account.")

        # Attempt to log in with Twilio
        twilio_client = TwilioClient(sid, auth_token)
        # Verify credentials by fetching account details
        account = twilio_client.api.accounts(sid).fetch()

        # Get user info properly
        user_info = message.from_user
        full_name = clean_text(f"{user_info.first_name} {user_info.last_name or ''}".strip())

        # Save login data to MongoDB
        await logindb_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "full_name": full_name,
                "sid": sid,
                "auth_token": auth_token,
                "logged_in": True
            }},
            upsert=True
        )

        LOGGER.info(f"User {user_id} logged in successfully.")
        await sent.edit(
            "**Successfully Logged In To Twilio Account ✅**",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        LOGGER.error(f"Login error for user {user_id}: {e}")
        await sent.edit(
            "**❌ Sorry Invalid Credentials Provided**",
            parse_mode=ParseMode.MARKDOWN
        )

@Client.on_message(
    filters.text & 
    filters.private & 
    filters.regex(r"^\🔐 Login$")  # Only match exact text "🔐 Login"
)
async def login_text_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_authorized(user_id):
        return await message.reply(
            "**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
            ])
        )

    user_states[user_id] = {"step": "awaiting_credentials"}
    return await message.reply(
        "**Now Please Provide Your SID and AUTH Token**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_login_{user_id}")]
        ])
    )

@Client.on_message(
    filters.text & 
    filters.private & 
    ~filters.command([], prefixes=COMMAND_PREFIX) &  # Exclude all commands
    ~filters.regex(r"^\🔐 Login$") &  # Exclude "🔐 Login" text
    filters.create(lambda _, __, message: message.from_user.id in user_states)  # Only for users in login state
)
async def handle_text_input(client: Client, message: Message):
    user_id = message.from_user.id
    state = user_states[user_id]
    text = message.text.strip()

    if state["step"] == "awaiting_credentials":
        args = text.split(maxsplit=1)
        if len(args) != 2:
            return await message.reply(
                "**Please provide both SID and Auth Token separated by a space ❌**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_login_{user_id}")]
                ])
            )

        sid, auth_token = args
        sent = await message.reply(
            "**Logging To Twilio Account...**",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            # Check if user is already logged in and log them out
            existing_user = await logindb_collection.find_one({"user_id": user_id})
            if existing_user and existing_user.get("logged_in", False):
                await logindb_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"logged_in": False}}
                )
                LOGGER.info(f"User {user_id} automatically logged out from previous account.")

            # Attempt to log in with Twilio
            twilio_client = TwilioClient(sid, auth_token)
            # Verify credentials by fetching account details
            account = twilio_client.api.accounts(sid).fetch()

            # Get user info properly
            user_info = message.from_user
            full_name = clean_text(f"{user_info.first_name} {user_info.last_name or ''}".strip())

            # Save login data to MongoDB
            await logindb_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id,
                    "full_name": full_name,
                    "sid": sid,
                    "auth_token": auth_token,
                    "logged_in": True
                }},
                upsert=True
            )

            LOGGER.info(f"User {user_id} logged in successfully.")
            # Clean up user state
            del user_states[user_id]

            await sent.edit(
                "**Successfully Logged In To Twilio Account ✅**",
                parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            LOGGER.error(f"Login error for user {user_id}: {e}")
            # Clean up user state on error
            if user_id in user_states:
                del user_states[user_id]

            await sent.edit(
                "**❌ Sorry Invalid Credentials Provided**",
                parse_mode=ParseMode.MARKDOWN
            )

@Client.on_callback_query(filters.regex(r"cancel_login_\d+"))
async def cancel_login(client: Client, query):
    user_id = query.from_user.id

    # Extract user_id from callback data for verification
    try:
        callback_user_id = int(query.data.split("_")[-1])
        if user_id != callback_user_id:
            return await query.answer("Not authorized to cancel this process.", show_alert=True)
    except (ValueError, IndexError):
        return await query.answer("Invalid callback data.", show_alert=True)

    # Clean up user state
    if user_id in user_states:
        del user_states[user_id]

    await query.message.edit_text(
        "**❌ Process Cancelled! You Can Start Again With /login**",
        parse_mode=ParseMode.MARKDOWN
    )
    await query.answer("Login process cancelled.")

@Client.on_message(filters.command(["logout"], prefixes=COMMAND_PREFIX) & filters.private)
async def logout_command(client: Client, message: Message):
    user_id = message.from_user.id

    if not await is_authorized(user_id):
        return await message.reply(
            "**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
            ])
        )

    try:
        # Check if user is logged in
        user_doc = await logindb_collection.find_one({"user_id": user_id})
        if not user_doc or not user_doc.get("logged_in", False):
            LOGGER.info(f"Logout attempt for user {user_id}: No active login found.")
            return await message.reply(
                "**You are not logged in! Use /login to log in first. ❌**",
                parse_mode=ParseMode.MARKDOWN
            )

        # Update the document to set logged_in to False
        result = await logindb_collection.update_one(
            {"user_id": user_id},
            {"$set": {"logged_in": False}}
        )

        LOGGER.info(f"Logout attempt for user {user_id}: modified_count={result.modified_count}")

        if result.modified_count > 0:
            LOGGER.info(f"User {user_id} logged out successfully.")

            # Also clean up any active login state
            if user_id in user_states:
                del user_states[user_id]

            return await message.reply(
                "**Successfully Logged Out From Account ✅**",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            LOGGER.warning(f"Logout for user {user_id}: No document was modified.")
            return await message.reply(
                "**You were already logged out! ⚠️**",
                parse_mode=ParseMode.MARKDOWN
            )

    except Exception as e:
        LOGGER.error(f"Logout error for user {user_id}: {e}")
        return await message.reply(
            "**Sorry Failed To Logout Due To Database Error ❌**",
            parse_mode=ParseMode.MARKDOWN
        )