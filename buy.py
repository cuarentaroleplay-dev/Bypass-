#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import ADMIN_IDS, COMMAND_PREFIX, DEVELOPER_ID
from core import authusers_collection, logindb_collection, numbersdb_collection
from utils import LOGGER
import aiohttp
import base64
from urllib.parse import quote
import asyncio
from datetime import datetime
import re

custom_area_states = {}

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

async def cleanup_old_account_numbers(user_id):
    user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
    if not user_data:
        return
    
    current_sid = user_data["sid"]
    
    result = await numbersdb_collection.delete_many({
        "user_id": user_id,
        "account_sid": {"$ne": current_sid}
    })
    if result.deleted_count > 0:
        LOGGER.info(f"Removed {result.deleted_count} numbers from old accounts for user {user_id}")

@Client.on_message(filters.command("buy", prefixes=COMMAND_PREFIX) & filters.private & authorized_only())
async def buy_command(client, message):
    user_id = message.from_user.id

    if not await is_logged_in(user_id):
        await message.reply(
            "**Please First Login Using /login**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Developer", user_id=DEVELOPER_ID)]
            ])
        )
        return

    await cleanup_old_account_numbers(user_id)

    await message.reply(
        "🛒 **Choose A Country Below:**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇺🇸 United States", callback_data="country_us"),
                InlineKeyboardButton("🇵🇷 Puerto Rico", callback_data="country_pr")
            ],
            [
                InlineKeyboardButton("🇨🇦 Canada", callback_data="country_ca"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu")
            ],
            [
                InlineKeyboardButton("Custom Area Code 💸", callback_data="custom_area_code")
            ]
        ])
    )

@Client.on_message(filters.text & filters.regex(r"🔍 Search Number") & filters.private & authorized_only())
async def search_number_text(client, message):
    user_id = message.from_user.id

    if not await is_logged_in(user_id):
        await message.reply(
            "**Please First Login Using /login**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Developer", user_id=DEVELOPER_ID)]
            ])
        )
        return

    await cleanup_old_account_numbers(user_id)

    await message.reply(
        "🛒 **Choose A Country Below:**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇺🇸 United States", callback_data="country_us"),
                InlineKeyboardButton("🇵🇷 Puerto Rico", callback_data="country_pr")
            ],
            [
                InlineKeyboardButton("🇨🇦 Canada", callback_data="country_ca"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu")
            ],
            [
                InlineKeyboardButton("Custom Area Code 💸", callback_data="custom_area_code")
            ]
        ])
    )

@Client.on_message(filters.text & filters.regex(r"💰 Custom Area Code") & filters.private & authorized_only())
async def custom_area_code_text(client, message):
    user_id = message.from_user.id

    # Check if user is logged in
    if not await is_logged_in(user_id):
        await message.reply(
            "**Please First Login Using /login**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Developer", user_id=DEVELOPER_ID)]
            ])
        )
        return

    # Clean up numbers from old accounts
    await cleanup_old_account_numbers(user_id)

    await message.reply(
        "**Please Choose The Country For Custom Numbers**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇺🇸 United States", callback_data="custom_country_us"),
                InlineKeyboardButton("🇵🇷 Puerto Rico", callback_data="custom_country_pr")
            ],
            [
                InlineKeyboardButton("🇨🇦 Canada", callback_data="custom_country_ca"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu")
            ]
        ])
    )

@Client.on_message(filters.text & filters.regex(r"Delete Number 🗑") & filters.private & authorized_only())
async def delete_number_text(client, message):
    user_id = message.from_user.id

    if not await is_logged_in(user_id):
        await message.reply(
            "**Please First Login Using /login**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Developer", user_id=DEVELOPER_ID)]
            ])
        )
        return

    await cleanup_old_account_numbers(user_id)

    numbers = await numbersdb_collection.find({"user_id": user_id}).to_list(None)

    if not numbers:
        await message.reply("**Sorry Bro No Number Purchased**", parse_mode=ParseMode.MARKDOWN)
        return

    buttons = []
    for i, number in enumerate(numbers):
        if i % 2 == 0:
            buttons.append([])
        buttons[-1].append(InlineKeyboardButton(
            number["phone_number"],
            callback_data=f"del_{quote(number['phone_number'])}"
        ))

    await message.reply(
        "**Please Select A Number To Delete 👇**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.text & filters.regex(r"🔍 Search Number|💰 Custom Area Code|Delete Number 🗑") & filters.private & ~authorized_only())
async def unauthorized_text_access(client, message):
    await message.reply(
        "**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
        ])
    )

@Client.on_callback_query(filters.regex("custom_area_code"))
async def custom_area_code_handler(client, callback_query):
    user_id = callback_query.from_user.id
    
    if not await is_logged_in(user_id):
        await callback_query.message.edit("**Please First Login Using /login**")
        return

    await cleanup_old_account_numbers(user_id)

    await callback_query.message.edit(
        "**Please Choose The Country For Custom Numbers**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇺🇸 United States", callback_data="custom_country_us"),
                InlineKeyboardButton("🇵🇷 Puerto Rico", callback_data="custom_country_pr")
            ],
            [
                InlineKeyboardButton("🇨🇦 Canada", callback_data="custom_country_ca"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu")
            ]
        ])
    )

@Client.on_callback_query(filters.regex(r"custom_country_(us|pr|ca)"))
async def custom_country_handler(client, callback_query):
    user_id = callback_query.from_user.id
    country_code = callback_query.data.split("_")[2].upper()
    country_map = {"US": "United States 🇺🇸", "PR": "Puerto Rico 🇵🇷", "CA": "Canada 🇨🇦"}
    country_name = country_map[country_code]

    custom_area_states[user_id] = {
        "step": "awaiting_digit_selection",
        "country_code": country_code,
        "country_name": country_name
    }

    await callback_query.message.edit(
        "**Please Select The Number Of Area Code Digits**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("3 Digit", callback_data="digit_3"),
                InlineKeyboardButton("6 Digit", callback_data="digit_6")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_custom_{user_id}")
            ]
        ])
    )

@Client.on_callback_query(filters.regex(r"digit_(3|6)"))
async def digit_selection_handler(client, callback_query):
    user_id = callback_query.from_user.id
    digit_count = callback_query.data.split("_")[1]

    if user_id not in custom_area_states:
        await callback_query.message.edit("**Session expired. Please start again.**")
        return

    custom_area_states[user_id]["step"] = "awaiting_area_code"
    custom_area_states[user_id]["digit_count"] = int(digit_count)

    await callback_query.message.edit(
        f"**Please Send The {digit_count} Digit Area Code**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_custom_{user_id}")]
        ])
    )

@Client.on_callback_query(filters.regex(r"cancel_custom_\d+"))
async def cancel_custom_area_code(client, callback_query):
    user_id = callback_query.from_user.id
    
    try:
        callback_user_id = int(callback_query.data.split("_")[-1])
        if user_id != callback_user_id:
            return await callback_query.answer("Not authorized to cancel this process.", show_alert=True)
    except (ValueError, IndexError):
        return await callback_query.answer("Invalid callback data.", show_alert=True)

    # Clean up user state
    if user_id in custom_area_states:
        del custom_area_states[user_id]
    
    await callback_query.message.edit(
        "**Custom Area Code Number Purchase Cancelled**",
        parse_mode=ParseMode.MARKDOWN
    )
    await callback_query.answer("Process cancelled.")

@Client.on_message(
    filters.text & 
    filters.private & 
    ~filters.command([], prefixes=COMMAND_PREFIX) &  
    filters.create(lambda _, __, message: message.from_user.id in custom_area_states)  
)
async def handle_area_code_input(client, message):
    user_id = message.from_user.id
    state = custom_area_states[user_id]
    text = message.text.strip()

    if state["step"] == "awaiting_area_code":
        digit_count = state["digit_count"]
        
        if not re.match(rf'^\d{{{digit_count}}}$', text):
            await message.reply(
                f"**Please Provide A Valid {digit_count}-Digit Integer**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_custom_{user_id}")]
                ])
            )
            return

        area_code = text
        country_code = state["country_code"]
        country_name = state["country_name"]

        
        del custom_area_states[user_id]

        
        sent = await message.reply(
            f"**Fetching Numbers With {digit_count}-Digit Area Code {area_code} For {country_name}**",
            parse_mode=ParseMode.MARKDOWN
        )

        
        user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
        if not user_data:
            await sent.edit("**Please First Login Using /login**")
            return

        
        sid = user_data["sid"]
        auth_token = user_data["auth_token"]
        headers = {"Authorization": get_auth_header(sid, auth_token)}
        base_url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/AvailablePhoneNumbers/{country_code}/Local.json?PageSize=50"

        
        if digit_count == 3 and country_code in ["US", "CA"]:
            url = f"{base_url}&AreaCode={area_code}"
        else:
            url = f"{base_url}&Contains={area_code}*"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        
                        if digit_count == 3 and country_code in ["US", "CA"]:
                            url = f"{base_url}&Contains={area_code}*"
                            async with session.get(url, headers=headers) as fallback_response:
                                if fallback_response.status != 200:
                                    raise Exception(f"API error: {fallback_response.status}")
                                data = await fallback_response.json()
                        else:
                            raise Exception(f"API error: {response.status}")
                    else:
                        data = await response.json()

                    matching_numbers = data.get("available_phone_numbers", [])

            if not matching_numbers:
                await sent.edit(
                    f"**No Available {country_name} Numbers Found With {digit_count}-Digit Area Code {area_code} ❌**",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

           
            text = f"**Available {country_name} Numbers With {digit_count}-Digit Area Code {area_code} ✅**\n**━━━━━━━━━━━━━━━━━━━━**\n"
            for i, number in enumerate(matching_numbers, 1):
                text += f"{number['phone_number']}\n"
            text += "**━━━━━━━━━━━━━━━━━━━━**\n**Select a number to purchase:👇**"

            buttons = []
            for i, number in enumerate(matching_numbers):
                if i % 2 == 0:
                    buttons.append([])
                buttons[-1].append(InlineKeyboardButton(
                    number["phone_number"],
                    callback_data=f"buy_{country_code}_{quote(number['phone_number'])}"
                ))

            await sent.edit(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        except Exception as e:
            LOGGER.error(f"Failed to fetch custom area code numbers for {user_id}: {e}")
            await sent.edit(
                f"**Failed to Fetch {country_name} Numbers With {digit_count}-Digit Area Code {area_code} ❌**",
                parse_mode=ParseMode.MARKDOWN
            )

@Client.on_callback_query(filters.regex(r"country_(us|pr|ca)"))
async def fetch_numbers(client, callback_query):
    user_id = callback_query.from_user.id
    country_code = callback_query.data.split("_")[1].upper()
    country_map = {"US": "United States 🇺🇸", "PR": "Puerto Rico 🇵🇷", "CA": "Canada 🇨🇦"}
    country_name = country_map[country_code]

    
    user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
    if not user_data:
        await callback_query.message.edit("**Please First Login Using /login**")
        return

    
    await cleanup_old_account_numbers(user_id)

    
    await callback_query.message.edit(f"**Fetching Numbers For Country {country_name}**", parse_mode=ParseMode.MARKDOWN)

    
    sid = user_data["sid"]
    auth_token = user_data["auth_token"]
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/AvailablePhoneNumbers/{country_code}/Local.json?PageSize=50"
    headers = {"Authorization": get_auth_header(sid, auth_token)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                data = await response.json()
                numbers = data.get("available_phone_numbers", [])

        if not numbers:
            await callback_query.message.edit(f"**No Available {country_name} Numbers Found ❌**", parse_mode=ParseMode.MARKDOWN)
            return

        
        text = f"**Available {country_name} Numbers ✅**\n**━━━━━━━━━━━━━━━━━━━━**\n"
        for i, number in enumerate(numbers, 1):
            text += f"{number['phone_number']}\n"
        text += "**━━━━━━━━━━━━━━━━━━━━**\n**Select a number to purchase:👇**"

        buttons = []
        for i, number in enumerate(numbers):
            if i % 2 == 0:
                buttons.append([])
            buttons[-1].append(InlineKeyboardButton(
                number["phone_number"],
                callback_data=f"buy_{country_code}_{quote(number['phone_number'])}"
            ))

        await callback_query.message.edit(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        LOGGER.error(f"Failed to fetch numbers for {user_id}: {e}")
        await callback_query.message.edit(f"**Failed to Fetch {country_name} Numbers ❌**", parse_mode=ParseMode.MARKDOWN)

@Client.on_callback_query(filters.regex(r"buy_"))
async def purchase_number(client, callback_query):
    user_id = callback_query.from_user.id
    _, country_code, phone_number = callback_query.data.split("_", 2)
    phone_number = phone_number.replace("%2B", "+")  

    
    user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
    if not user_data:
        await callback_query.message.reply("**Please First Login Using /login**", parse_mode=ParseMode.MARKDOWN)
        return

  
    sid = user_data["sid"]
    auth_token = user_data["auth_token"]
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json"
    headers = {
        "Authorization": get_auth_header(sid, auth_token),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "PhoneNumber": phone_number,
        "SmsEnabled": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 201:
                    raise Exception(f"Purchase failed: {response.status}")
                purchase_data = await response.json()
                phone_sid = purchase_data.get("sid")

        
        await numbersdb_collection.insert_one({
            "user_id": user_id,
            "phone_number": phone_number,
            "phone_sid": phone_sid,
            "account_sid": sid,  
            "country_code": country_code,
            "purchase_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        
        await callback_query.message.reply(
            f"**Successfully Purchased Number {phone_number} ✅**",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        LOGGER.error(f"Failed to purchase number {phone_number} for {user_id}: {e}")
        await callback_query.message.reply(
            "**Failed To Purchase Number ❌**",
            parse_mode=ParseMode.MARKDOWN
        )

@Client.on_callback_query(filters.regex("close_menu"))
async def close_menu(client, callback_query):
    await callback_query.message.delete()

@Client.on_message(filters.command("my", prefixes=COMMAND_PREFIX) & filters.private & authorized_only())
async def my_numbers(client, message):
    user_id = message.from_user.id

    
    await cleanup_old_account_numbers(user_id)

    
    numbers = await numbersdb_collection.find({"user_id": user_id}).to_list(None)

    if not numbers:
        await message.reply("**Sorry Bro No Number Purchased**", parse_mode=ParseMode.MARKDOWN)
        return

    text = "**Your Purchased Numbers ✅**\n**━━━━━━━━━━━━━━━━━━━━**\n"
    for i, number in enumerate(numbers, 1):
        text += f"**{i}.** {number['phone_number']} ({number['country_code']})\n"
        text += f"**Purchased:** {number['purchase_time']}\n"
        text += "**━━━━━━━━━━━━━━━━━━━━**\n"

    await message.reply(text, parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("del", prefixes=COMMAND_PREFIX) & filters.private & authorized_only())
async def delete_number_command(client, message):
    user_id = message.from_user.id

    
    await cleanup_old_account_numbers(user_id)

    
    numbers = await numbersdb_collection.find({"user_id": user_id}).to_list(None)

    if not numbers:
        await message.reply("**Sorry Bro No Number Purchased**", parse_mode=ParseMode.MARKDOWN)
        return

    
    buttons = []
    for i, number in enumerate(numbers):
        if i % 2 == 0:
            buttons.append([])
        buttons[-1].append(InlineKeyboardButton(
            number["phone_number"],
            callback_data=f"del_{quote(number['phone_number'])}"
        ))

    await message.reply(
        "**Please Select A Number To Delete 👇**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"del_"))
async def delete_number(client, callback_query):
    user_id = callback_query.from_user.id
    phone_number = callback_query.data.split("_", 1)[1].replace("%2B", "+")  

    
    user_data = await logindb_collection.find_one({"user_id": user_id, "logged_in": True})
    if not user_data:
        await callback_query.message.edit("**Please First Login Using /login**")
        return

    
    number_data = await numbersdb_collection.find_one({"user_id": user_id, "phone_number": phone_number})
    if not number_data:
        await callback_query.message.edit("**Number Not Found ❌**", parse_mode=ParseMode.MARKDOWN)
        return

    
    sent = await callback_query.message.edit(f"**Deleting Number {phone_number}**", parse_mode=ParseMode.MARKDOWN)

    
    sid = user_data["sid"]
    auth_token = user_data["auth_token"]
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json"
    headers = {"Authorization": get_auth_header(sid, auth_token)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch numbers: {response.status}")
                data = await response.json()
                phone_sid = None
                for record in data.get("incoming_phone_numbers", []):
                    if record["phone_number"] == phone_number:
                        phone_sid = record["sid"]
                        break

            if not phone_sid:
                raise Exception("Phone SID not found")

            
            delete_url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers/{phone_sid}.json"
            async with session.delete(delete_url, headers=headers) as delete_response:
                if delete_response.status != 204:
                    raise Exception(f"Failed to delete number: {delete_response.status}")

        await numbersdb_collection.delete_one({"user_id": user_id, "phone_number": phone_number})

        await sent.edit("**Successfully Deleted Number ✅**", parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        LOGGER.error(f"Failed to delete number {phone_number} for {user_id}: {e}")
        await sent.edit("**Sorry Unable To Delete Number ❌**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command(["buy", "my", "del"], prefixes=COMMAND_PREFIX) & filters.private & ~authorized_only())
async def unauthorized_access(client, message):
    await message.reply(
        "**Sorry Bro You Are Not Authorized ❌ DM @Saddam_XD For Auth**",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner", user_id=DEVELOPER_ID)]
        ])
    )