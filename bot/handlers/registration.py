from aiogram import Router, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

from bot.database.models import get_session, User, Application
from bot.utils.config import Config
from bot.utils.roles import UserRole
from bot.keyboards.registration import application_kb
from bot.keyboards.main_menu import main_menu_kb

router = Router()

class Registration(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    with get_session() as session:
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        
        # Если пользователь уже имеет доступ
        if user and user.status in [UserRole.WORKER, UserRole.MENTOR, UserRole.ADMIN]:
            await message.answer_photo(
                photo=FSInputFile(Config.MENU_PHOTO_PATH),
                caption="🚀 Главное меню",
                reply_markup=main_menu_kb(message.from_user.id)
            )
            return
        
        # Если заявка уже на рассмотрении
        if user and user.status == UserRole.PENDING:
            await message.answer("⏳ Ваша заявка уже на рассмотрении. Ожидайте одобрения.")
            return
    
    # Начало процесса регистрации
    await state.set_state(Registration.question1)
    await message.answer(
        "📝 Для доступа к боту ответьте на 3 вопроса:\n\n"
        "1. Расскажите о своем опыте работы?",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Registration.question1)
async def process_question1(message: Message, state: FSMContext):
    if len(message.text) < 10:
        return await message.answer("❌ Ответ должен содержать минимум 10 символов")
    
    await state.update_data(answer1=message.text)
    await state.set_state(Registration.question2)
    await message.answer("2. Почему вы хотите присоединиться к команде?")

@router.message(Registration.question2)
async def process_question2(message: Message, state: FSMContext):
    if len(message.text) < 10:
        return await message.answer("❌ Ответ должен содержать минимум 10 символов")
    
    await state.update_data(answer2=message.text)
    await state.set_state(Registration.question3)
    await message.answer("3. Какие направления работы вам интересны?")

@router.message(Registration.question3)
async def process_question3(message: Message, state: FSMContext):
    if len(message.text) < 5:
        return await message.answer("❌ Ответ должен содержать минимум 5 символов")
    
    data = await state.get_data()
    
    with get_session() as session:
        # Создаем или обновляем пользователя
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        if not user:
            user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                status=UserRole.PENDING,
                registration_date=datetime.now()
            )
            session.add(user)
        
        # Создаем заявку
        application = Application(
            user_id=user.id,
            answer1=data['answer1'],
            answer2=data['answer2'],
            answer3=message.text,
            created_at=datetime.now()
        )
        session.add(application)
        session.commit()
    
    # Отправляем заявку админам
    app_text = (
        "📄 *Новая заявка на доступ*\n\n"
        f"👤 Пользователь: @{message.from_user.username or 'нет'}\n"
        f"🆔 ID: {message.from_user.id}\n\n"
        "1. *Опыт работы:*\n" + data['answer1'] + "\n\n"
        "2. *Причины присоединения:*\n" + data['answer2'] + "\n\n"
        "3. *Интересующие направления:*\n" + message.text
    )
    
    try:
        await message.bot.send_message(
            chat_id=Config.ADMIN_CHAT_ID,
            text=app_text,
            parse_mode="Markdown",
            reply_markup=application_kb(user.id)
        )
    except Exception as e:
        print(f"Ошибка отправки заявки: {e}")
    
    await state.clear()
    await message.answer(
        "✅ Ваша заявка отправлена на рассмотрение! Ожидайте одобрения.",
        reply_markup=ReplyKeyboardRemove()
    )