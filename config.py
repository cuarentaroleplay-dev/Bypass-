#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev
import os
from dotenv import load_dotenv

load_dotenv()

def get_env_or_default(key, default=None, cast_func=str):
    value = os.getenv(key)
    if value is not None and value.strip() != "":
        try:
            return cast_func(value)
        except (ValueError, TypeError) as e:
            print(f"Error casting {key} with value '{value}' to {cast_func.__name__}: {e}")
            return default
    return default

API_ID = get_env_or_default("API_ID", default=None, cast_func=int)
API_HASH = get_env_or_default("API_HASH")
BOT_TOKEN = get_env_or_default("BOT_TOKEN")
DEVELOPER_ID = get_env_or_default("DEVELOPER_ID", default=None, cast_func=int)
UPDATE_CHANNEL_URL = get_env_or_default("UPDATE_CHANNEL_URL")
ADMIN_IDS = get_env_or_default("ADMIN_IDS", default="", cast_func=str)
COMMAND_PREFIX = get_env_or_default("COMMAND_PREFIX", default=".,/,!,#", cast_func=str).split(",")
MONGO_URL = get_env_or_default("MONGO_URL")

ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]

required_vars = {
    "API_ID": 33300028,
    "API_HASH": a34eac607c3502c25867dcc1eb485832,
    "BOT_TOKEN": 8615740285:AAFqQ6p9GFswqs1TWCH7Bu9npgrw8NDhjtk,
    "DEVELOPER_ID": 7008799336,
    "UPDATE_CHANNEL_URL": UPDATE_CHANNE.www.com,
    "MONGO_URL": mongodb://localhost:27017,
}

for var_name, var_value in required_vars.items():
    if var_value is None or var_value == f"Your_{var_name}_Here" or (isinstance(var_value, str) and var_value.strip() == ""):
        raise ValueError(f"Required variable {var_name} is missing or invalid. Set it in .env (VPS), config.py (VPS), or Heroku config vars.")

print("Loaded COMMAND_PREFIX:", COMMAND_PREFIX)
if not COMMAND_PREFIX:
    raise ValueError("No command prefixes found. Set COMMAND_PREFIX in .env, config.py, or Heroku config vars.")
