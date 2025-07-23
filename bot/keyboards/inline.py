from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def mentor_request_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_mentor_{user_id}"),
                InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_mentor_{user_id}")
            ]
        ]
    )