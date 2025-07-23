import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("BOT_TOKEN", "7896652255:AAEoVDmvJX1qLcY6YDIRykL2aGE-pPUXGzg")
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", -1002884890321))
    LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", -1002851919470))
    PROFIT_CHAT_ID = int(os.getenv("PROFIT_CHAT_ID", -1002822326364))
    DB_PATH = os.getenv("DB_PATH", "bd/database.db")
    PHOTO_PATH = os.getenv("PHOTO_PATH", "photo/profile.png")
    MENU_PHOTO_PATH = os.getenv("MENU_PHOTO_PATH", "photo/ntv.png")