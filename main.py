#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev
from app import app
from utils import LOGGER
from config import DEVELOPER_ID
from pyrogram import idle
import asyncio

async def main():
    await app.start()
    LOGGER.info("Bot Successfully Started💥")
    if DEVELOPER_ID:
        try:
            await app.send_message(
                int(DEVELOPER_ID),
                "**Bot Successfully Started💥**"
            )
            LOGGER.info(f"Sent startup confirmation to DEVELOPER_ID: {DEVELOPER_ID}")
        except Exception as e:
            LOGGER.error(f"Could not send startup message to DEVELOPER_ID: {e}")
            LOGGER.error("Please ensure DEVELOPER_ID is a valid user ID and the bot can message them.")
    await idle()
    await app.stop()
    LOGGER.info("Bot Stopped Successfully.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())