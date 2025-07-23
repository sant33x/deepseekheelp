from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.database.models import User, Session
from bot.utils.roles import UserRole

def main_menu_kb(user_id: int = None):
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="👤 Мой профиль")
    builder.button(text="📋 Меню")
    builder.button(text="ℹ️ Информация")
    
    if user_id:
        with Session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user and user.status == UserRole.MENTOR:
                builder.button(text="📝 Анкета наставника")
    
    builder.button(text="🏷️ Кастом тег")
    
    builder.adjust(1, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def profile_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

def info_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📰 Новости"), KeyboardButton(text="💸 Канал профитов")],
            [KeyboardButton(text="💬 Чат воркеров"), KeyboardButton(text="👨‍🏫 Наставники")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )