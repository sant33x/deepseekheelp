from aiogram.utils.keyboard import InlineKeyboardBuilder

def application_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Одобрить", callback_data=f"app_approve_{user_id}")
    builder.button(text="❌ Отклонить", callback_data=f"app_reject_{user_id}")
    builder.adjust(2)
    return builder.as_markup()