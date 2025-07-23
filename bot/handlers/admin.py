from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from sqlalchemy import func

from bot.database.models import get_session, User, Profit, Mentor, Application
from bot.utils.config import Config
from bot.utils.roles import UserRole
from bot.keyboards.registration import application_kb
from bot.keyboards.main_menu import main_menu_kb

router = Router()

async def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    with get_session() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        return user and user.status == UserRole.ADMIN

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("❌ Доступ только для администраторов")
    
    with get_session() as session:
        stats = {
            "users": session.query(User).count(),
            "workers": session.query(User).filter_by(status=UserRole.WORKER).count(),
            "mentors": session.query(User).filter_by(status=UserRole.MENTOR).count(),
            "pending": session.query(Application).count(),
            "profits": session.query(func.sum(Profit.amount)).scalar() or 0
        }
    
    text = (
        "⚙️ *Админ-панель*\n\n"
        f"👥 Всего пользователей: {stats['users']}\n"
        f"👷 Воркеров: {stats['workers']}\n"
        f"👨‍🏫 Наставников: {stats['mentors']}\n"
        f"📝 Заявок на рассмотрении: {stats['pending']}\n"
        f"💰 Общий профит: {stats['profits']} RUB\n\n"
        "Доступные команды:\n"
        "/help - список команд\n"
        "/users - список пользователей\n"
        "/applications - заявки"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("help"))
async def admin_help(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    help_text = (
        "📌 *Админ команды*\n\n"
        "👤 Управление пользователями:\n"
        "/setrole [id] [role] - Назначить роль\n"
        "/find [id] - Найти пользователя\n\n"
        "📝 Заявки:\n"
        "/applications - Список заявок\n"
        "/approve [id] - Одобрить заявку\n"
        "/reject [id] - Отклонить заявку\n\n"
        "💰 Профиты:\n"
        "/profit [id] [sum] [direction] [service] - Добавить профит\n"
        "/profits [id] - Статистика пользователя\n\n"
        "👨‍🏫 Наставники:\n"
        "/mentor [id] [direction] [%] - Назначить наставником\n"
        "/mentors - Список наставников\n\n"
        "Примеры:\n"
        "/setrole 123456 Наставник\n"
        "/profit 123456 5000 Обнал Binance\n"
        "/mentor 789123 Обнал 20"
    )
    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("applications"))
async def list_applications(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    with get_session() as session:
        apps = session.query(Application).order_by(Application.created_at.desc()).limit(10).all()
    
    if not apps:
        return await message.answer("Нет заявок на рассмотрении")
    
    text = "📝 *Последние 10 заявок:*\n\n"
    for app in apps:
        text += (
            f"🆔 {app.user_id} | {app.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"👉 {app.answer1[:30]}...\n\n"
        )
    
    await message.answer(text, parse_mode="Markdown")

@router.callback_query(F.data.startswith("app_"))
async def process_application(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("❌ Доступ запрещен", show_alert=True)
    
    action, user_id = callback.data.split("_")[1], int(callback.data.split("_")[2])
    
    with get_session() as session:
        user = session.query(User).get(user_id)
        if not user:
            return await callback.answer("Пользователь не найден")
        
        if action == "approve":
            user.status = UserRole.WORKER
            try:
                await callback.bot.send_message(
                    chat_id=user.user_id,
                    text="✅ *Ваша заявка одобрена!*\n\nТеперь вы можете пользоваться ботом.\nВведите /start",
                    parse_mode="Markdown",
                    reply_markup=main_menu_kb(user.user_id)
                )
            except Exception as e:
                print(f"Ошибка уведомления пользователя: {e}")
        else:
            user.status = UserRole.REJECTED
        
        session.query(Application).filter_by(user_id=user.id).delete()
        session.commit()
    
    await callback.answer(f"Заявка {'одобрена' if action == 'approve' else 'отклонена'}")
    await callback.message.edit_reply_markup(reply_markup=None)

@router.message(Command("setrole"))
async def set_role(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    try:
        _, user_id, role = message.text.split()
        user_id = int(user_id)
        role = UserRole[role.upper()]
    except ValueError:
        return await message.answer("❌ Неверный формат. Используйте: /setrole [id] [role]")
    except KeyError:
        return await message.answer(f"❌ Неверная роль. Доступные: {', '.join([r.value for r in UserRole])}")
    
    with get_session() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return await message.answer("❌ Пользователь не найден")
        
        user.status = role
        session.commit()
    
    await message.answer(f"✅ Роль {role.value} установлена для пользователя {user_id}")

@router.message(Command("profit"))
async def add_profit(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = float(parts[2])
        direction = ' '.join(parts[3:-1])
        service = parts[-1]
    except:
        return await message.answer(
            "❌ Неверный формат. Используйте:\n"
            "/profit [id] [sum] [direction] [service]\n"
            "Пример: /profit 123456 5000 Обнал Binance"
        )
    
    with get_session() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return await message.answer("❌ Пользователь не найден")
        
        profit = Profit(
            user_id=user.id,
            amount=amount,
            direction=direction,
            service=service,
            date=datetime.now()
        )
        session.add(profit)
        
        if user.mentor:
            mentor_profit = Profit(
                user_id=user.mentor.user_id,
                amount=amount * (user.mentor.commission / 100),
                direction=f"Комиссия от {user_id}",
                service=service,
                date=datetime.now()
            )
            session.add(mentor_profit)
        
        session.commit()
        
        profit_text = (
            "# 🦈 Успешное пополнение\n\n"
            f"├💸 Сумма: {amount} RUB\n"
            f"├⛏️ Воркер: @{user.username if user.username else user.user_id}\n"
        )
        
        if user.mentor:
            profit_text += f"├📚 Наставник: @{user.mentor.user.username}\n"
        
        profit_text += f"└💵 Сервис: {service}"
        
        await message.bot.send_message(
            chat_id=Config.PROFIT_CHAT_ID,
            text=profit_text
        )
    
    await message.answer(f"✅ Профит {amount} RUB добавлен для пользователя {user_id}")

@router.message(Command("mentor"))
async def set_mentor(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    try:
        _, user_id, direction, commission = message.text.split(maxsplit=3)
        user_id = int(user_id)
        commission = float(commission)
    except:
        return await message.answer(
            "❌ Неверный формат. Используйте:\n"
            "/mentor [id] [direction] [commission%]\n"
            "Пример: /mentor 789123 Обнал 20"
        )
    
    with get_session() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return await message.answer("❌ Пользователь не найден")
        
        mentor = session.query(Mentor).filter_by(user_id=user_id).first()
        if not mentor:
            mentor = Mentor(user_id=user_id)
            session.add(mentor)
        
        mentor.direction = direction
        mentor.commission = commission
        user.status = UserRole.MENTOR
        session.commit()
    
    await message.answer(
        f"✅ Пользователь {user_id} назначен наставником:\n"
        f"📍 Направление: {direction}\n"
        f"💸 Комиссия: {commission}%"
    )

@router.message(Command("mentors"))
async def list_mentors(message: Message):
    if not await is_admin(message.from_user.id):
        return
    
    with get_session() as session:
        mentors = session.query(Mentor).join(User).all()
    
    if not mentors:
        return await message.answer("❌ Нет зарегистрированных наставников")
    
    text = "👨‍🏫 *Список наставников:*\n\n"
    for mentor in mentors:
        text += (
            f"🆔 {mentor.user_id}\n"
            f"👤 @{mentor.user.username if mentor.user.username else 'нет'}\n"
            f"📍 {mentor.direction}\n"
            f"💸 {mentor.commission}%\n"
            f"📝 {mentor.description[:50] if mentor.description else 'нет описания'}...\n\n"
        )
    
    await message.answer(text, parse_mode="Markdown")