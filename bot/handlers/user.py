from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from datetime import datetime
from sqlalchemy import func

from bot.database.models import get_session, User, Profit
from bot.utils.config import Config
from bot.utils.roles import UserRole
from bot.keyboards.main_menu import main_menu_kb, profile_kb, info_kb
from bot.handlers.registration import check_user_access

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    if not await check_user_access(message.from_user.id):
        return
    
    with get_session() as session:
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        if not user:
            return await message.answer("❌ Пожалуйста, пройдите регистрацию через /start")
        
        if user.status == UserRole.PENDING:
            return await message.answer("⏳ Ваша заявка на рассмотрении. Ожидайте одобрения.")
        
        if user.status == UserRole.REJECTED:
            return await message.answer("❌ Ваша заявка отклонена. Доступ запрещен.")
    
    await message.answer_photo(
        photo=FSInputFile(Config.MENU_PHOTO_PATH),
        caption="🚀 Главное меню",
        reply_markup=main_menu_kb(message.from_user.id)
    )

@router.message(F.text == "👤 Мой профиль")
async def profile_handler(message: Message):
    if not await check_user_access(message.from_user.id):
        return
    
    with get_session() as session:
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        if not user:
            return await message.answer("❌ Профиль не найден")
        
        total_profit = session.query(func.sum(Profit.amount)).filter_by(user_id=user.id).scalar() or 0
        days_with_us = (datetime.now() - user.registration_date).days
        
        text = (
            f"👤 *Ваш профиль*\n\n"
            f"🆔 ID: {user.user_id}\n"
            f"📛 Статус: {user.status}\n"
            f"💰 Заработано: {total_profit} RUB\n"
            f"📅 С нами: {days_with_us} дней"
        )
        
        await message.answer_photo(
            photo=FSInputFile(Config.PHOTO_PATH),
            caption=text,
            reply_markup=profile_kb()
        )

@router.message(F.text == "📋 Меню")
async def menu_handler(message: Message):
    if not await check_user_access(message.from_user.id):
        return
    
    with get_session() as session:
        total_profit = session.query(func.sum(Profit.amount)).scalar() or 0
        profit_count = session.query(Profit).count()
        
        text = (
            "🏦 *Информация о профитах*\n\n"
            f"┏ Общая сумма: {total_profit} RUB\n"
            f"┗ Количество: {profit_count}\n\n"
            "👤 *Проценты воркера*\n"
            "┣ Тест - 80%\n"
            "┣ Тест - 75%\n"
            "┣ Тест - 65%\n"
            "┣ Тест - 60%\n"
            "┗ Тест - 15%\n\n"
            "📑 *Направления работы*\n"
            "┣ Направление 1 | Work📗\n"
            "┣ Направление 2 | Work📗\n"
            "┣ Направление 3 | Work📗\n"
            "┣ Направление 4 | Work📗\n"
            "┗ Направление 5 | Work📗"
        )
        
        await message.answer_photo(
            photo=FSInputFile(Config.MENU_PHOTO_PATH),
            caption=text,
            reply_markup=info_kb()
        )

@router.message(F.text == "📰 Новости")
async def news_handler(message: Message):
    if not await check_user_access(message.from_user.id):
        return
    await message.answer("📢 Наши новости: https://exclabs.pro/")

@router.message(F.text == "💸 Канал профитов")
async def profits_handler(message: Message):
    if not await check_user_access(message.from_user.id):
        return
    await message.answer("💰 Канал профитов: https://exclabs.pro/")

@router.message(F.text == "💬 Чат воркеров")
async def workers_chat_handler(message: Message):
    if not await check_user_access(message.from_user.id):
        return
    await message.answer("💬 Чат воркеров: https://exclabs.pro/")

@router.message(F.text == "⬅️ Назад")
async def back_handler(message: Message, state: FSMContext):
    if not await check_user_access(message.from_user.id):
        return
    
    await state.clear()
    await message.answer_photo(
        photo=FSInputFile(Config.MENU_PHOTO_PATH),
        caption="🚀 Главное меню",
        reply_markup=main_menu_kb(message.from_user.id)
    )