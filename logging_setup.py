#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev

import logging
import logging.handlers

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    'botlog.txt', maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

LOGGER.addHandler(console_handler)
LOGGER.addHandler(file_handler)

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

LOGGER.info("LOGGER Module Successfully Intailized")