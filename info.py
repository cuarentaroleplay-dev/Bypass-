# Copyright @ISmartDevs
# Channel t.me/TheSmartDev
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode, ChatType, UserStatus
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied, ChannelInvalid
from config import ADMIN_IDS, COMMAND_PREFIX, DEVELOPER_ID
from core import authusers_collection
from utils import LOGGER, get_dc_locations

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

# Function to calculate account age accurately
def calculate_account_age(creation_date):
    today = datetime.now()
    delta = relativedelta(today, creation_date)
    years = delta.years
    months = delta.months
    days = delta.days
    return f"{years} years, {months} months, {days} days"

# Function to estimate account creation date based on user ID
def estimate_account_creation_date(user_id):
    reference_points = [
        (100000000, datetime(2013, 8, 1)),  # Telegram's launch date
        (1273841502, datetime(2020, 8, 13)),  # Example reference point
        (1500000000, datetime(2021, 5, 1)),  # Another reference point
        (2000000000, datetime(2022, 12, 1)),  # Another reference point
    ]
    
    closest_point = min(reference_points, key=lambda x: abs(x[0] - user_id))
    closest_user_id, closest_date = closest_point
    id_difference = user_id - closest_user_id
    days_difference = id_difference / 20000000  # Assuming 20M user IDs per day
    creation_date = closest_date + timedelta(days=days_difference)
    return creation_date

@Client.on_message(filters.command(["info", "id"], prefixes=COMMAND_PREFIX) & filters.private & authorized_only())
async def handle_info_command(client, message):
    LOGGER.info("Received /info or /id command")

    try:
        DC_LOCATIONS = get_dc_locations()
        progress_message = await client.send_message(
            message.chat.id,
            "<b>Fetching Info From Database...</b>",
            parse_mode=ParseMode.HTML
        )

        # Handle different cases: current user, replied user/bot, or provided username
        if not message.command or (len(message.command) == 1 and not message.reply_to_message):
            LOGGER.info("Fetching current user info")
            user = message.from_user
            chat = message.chat
            await process_user_info(client, message, progress_message, user, chat, DC_LOCATIONS)

        elif message.reply_to_message:
            LOGGER.info("Fetching info of the replied user or bot")
            user = message.reply_to_message.from_user
            chat = message.chat
            await process_user_info(client, message, progress_message, user, chat, DC_LOCATIONS)

        elif len(message.command) > 1:
            username = message.command[1].strip('@').replace('https://', '').replace('http://', '').replace('t.me/', '').replace('/', '').replace(':', '')
            LOGGER.info(f"Fetching info for user, bot, or chat: {username}")

            try:
                # Try user or bot info
                user = await client.get_users(username)
                await process_user_info(client, message, progress_message, user, message.chat, DC_LOCATIONS)
            except (PeerIdInvalid, UsernameNotOccupied):
                LOGGER.info(f"Username '{username}' not found as a user/bot. Checking for chat...")
                try:
                    chat = await client.get_chat(username)
                    await process_chat_info(client, message, progress_message, chat, DC_LOCATIONS)
                except (ChannelInvalid, PeerIdInvalid):
                    await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=progress_message.id,
                        text="<b>Sorry Bro User Invalid❌</b>",
                        parse_mode=ParseMode.HTML
                    )
                    LOGGER.error(f"Permission error for chat: {username}")
                except Exception as e:
                    await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=progress_message.id,
                        text="<b>Sorry Bro User Invalid❌</b>",
                        parse_mode=ParseMode.HTML
                    )
                    LOGGER.error(f"Error fetching chat info: {str(e)}")
            except Exception as e:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=progress_message.id,
                    text="<b>Sorry Bro User Invalid❌</b>",
                    parse_mode=ParseMode.HTML
                )
                LOGGER.error(f"Error fetching user/bot info: {str(e)}")

    except Exception as e:
        LOGGER.error(f"Unhandled exception: {str(e)}")
        await client.send_message(
            message.chat.id,
            "<b>Sorry Bro User Invalid❌</b>",
            parse_mode=ParseMode.HTML
        )

async def process_user_info(client, message, progress_message, user, chat, DC_LOCATIONS):
    premium_status = "Yes" if user.is_premium else "No"
    dc_location = DC_LOCATIONS.get(user.dc_id, "Unknown")
    account_created = estimate_account_creation_date(user.id)
    account_created_str = account_created.strftime("%B %d, %Y")
    account_age = calculate_account_age(account_created)
    verified_status = "Yes" if getattr(user, 'is_verified', False) else "No"
    
    # Check authorization status
    authorized_status = "Yes" if await is_authorized_user(user.id) else "No"

    status = "Unknown"
    if user.status:
        if user.status == UserStatus.ONLINE:
            status = "Online"
        elif user.status == UserStatus.OFFLINE:
            status = "Offline"
        elif user.status == UserStatus.RECENTLY:
            status = "Recently online"
        elif user.status == UserStatus.LAST_WEEK:
            status = "Last seen within week"
        elif user.status == UserStatus.LAST_MONTH:
            status = "Last seen within month"

    response = (
        "<b>Smart Twilio User Info From Database✅</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>⊗ Full Name:</b> {user.first_name} {user.last_name or ''}\n"
        f"<b>⊗ ID:</b> <code>{user.id}</code>\n"
        f"<b>⊗ Chat ID:</b> <code>{chat.id}</code>\n"
        f"<b>⊗ Data Center:</b> {user.dc_id} ({dc_location})\n"
        f"<b>⊗ Premium:</b> {premium_status}\n"
        f"<b>⊗ Verification:</b> {verified_status}\n"
        f"<b>⊗ Authorized:</b> {authorized_status}\n"
        f"<b>⊗ Flags:</b> {'Scam' if getattr(user, 'is_scam', False) else 'Fake' if getattr(user, 'is_fake', False) else 'Clean'}\n"
        f"<b>⊗ Status:</b> {status}\n"
        f"<b>⊗ Account Created On:</b> {account_created_str}\n"
        f"<b>⊗ Account Age:</b> {account_age}\n"
        "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Smart Twilio User Info Check ➺ Successful✅</b>"
    )

    buttons = [[InlineKeyboardButton("Profile Info", user_id=user.id)]]
    if user.is_bot:
        response = (
            "<b>Smart Twilio Bot Info From Database✅</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<b>⊗ Bot Name:</b> {user.first_name} {user.last_name or ''}\n"
            f"<b>⊗ ID:</b> <code>{user.id}</code>\n"
            f"<b>⊗ Chat ID:</b> <code>{chat.id}</code>\n"
            f"<b>⊗ Data Center:</b> {user.dc_id} ({dc_location})\n"
            f"<b>⊗ Premium:</b> {premium_status}\n"
            f"<b>⊗ Verification:</b> {verified_status}\n"
            f"<b>⊗ Authorized:</b> {authorized_status}\n"
            f"<b>⊗ Flags:</b> {'Scam' if getattr(user, 'is_scam', False) else 'Fake' if getattr(user, 'is_fake', False) else 'Clean'}\n"
            f"<b>⊗ Status:</b> Bot\n"
            f"<b>⊗ Account Created On:</b> {account_created_str}\n"
            f"<b>⊗ Account Age:</b> {account_age}\n"
            "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
            "<b>Smart Twilio Bot Info Check ➺ Successful✅</b>"
        )

    await client.edit_message_text(
        chat_id=message.chat.id,
        message_id=progress_message.id,
        text=response,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    LOGGER.info("User/bot info fetched successfully")

async def process_chat_info(client, message, progress_message, chat, DC_LOCATIONS):
    chat_type = "Supergroup" if chat.type == ChatType.SUPERGROUP else "Group" if chat.type == ChatType.GROUP else "Channel"
    response = (
        "<b>Smart Twilio Chat Info From Database✅</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        f"⊗ Chat Name: {chat.title}\n"
        f"⊗ ID: <code>{chat.id}</code>\n"
        f"⊗ Type: {chat_type}\n"
        f"⊗ Member count: {chat.members_count if chat.members_count else 'Unknown'}\n"
        "<b>━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Smart Twilio Chat Info Check ➺ Successful✅</b>"
    )

    buttons = [[InlineKeyboardButton("Joining Link", url=f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(chat.id).replace('-100', '')}/1")]]
    await client.edit_message_text(
        chat_id=message.chat.id,
        message_id=progress_message.id,
        text=response,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    LOGGER.info("Chat info fetched successfully")

@Client.on_message(filters.command(["info", "id"], prefixes=COMMAND_PREFIX) & filters.private & ~authorized_only())
async def unauthorized_access(client, message):
    await message.reply(
        "<b>Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
        ])
    )
    LOGGER.info("Unauthorized access attempt for /info command")

@Client.on_message(filters.text & filters.private & filters.regex("^👤 Account$") & authorized_only())
async def handle_account_text(client, message):
    LOGGER.info("Received '👤 Account' text from authorized user")
    
    try:
        DC_LOCATIONS = get_dc_locations()
        progress_message = await client.send_message(
            message.chat.id,
            "<b>Fetching Info From Database...</b>",
            parse_mode=ParseMode.HTML
        )

        user = message.from_user
        chat = message.chat
        await process_user_info(client, message, progress_message, user, chat, DC_LOCATIONS)

    except Exception as e:
        LOGGER.error(f"Error in handle_account_text: {str(e)}")
        await client.send_message(
            message.chat.id,
            "<b>Sorry Bro User Invalid❌</b>",
            parse_mode=ParseMode.HTML
        )

@Client.on_message(filters.text & filters.private & filters.regex("^👤 Account$") & ~authorized_only())
async def handle_account_text_unauthorized(client, message):
    LOGGER.info("Received '👤 Account' text from unauthorized user")
    
    await message.reply(
        "<b>Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
        ])
    )