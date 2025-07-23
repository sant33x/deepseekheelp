from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.models import Session, Mentor, User
from bot.utils.config import Config
from bot.keyboards.main_menu import main_menu_kb
from bot.utils.roles import UserRole

router = Router()

class MentorForm(StatesGroup):
    direction = State()
    commission = State()
    description = State()

@router.message(F.text == "📝 Анкета наставника")
async def start_mentor_form(message: Message, state: FSMContext):
    with Session() as session:
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        if not user or user.status != UserRole.MENTOR:
            return await message.answer("Эта функция доступна только наставникам!")
    
    await state.set_state(MentorForm.direction)
    await message.answer(
        "📝 Заполнение анкеты наставника\n\n"
        "Укажите ваше направление работы:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(MentorForm.direction)
async def process_direction(message: Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(MentorForm.commission)
    await message.answer("Укажите ваш процент комиссии (только число, например 20):")

@router.message(MentorForm.commission)
async def process_commission(message: Message, state: FSMContext):
    try:
        commission = float(message.text)
        if commission <= 0 or commission > 100:
            raise ValueError
        await state.update_data(commission=commission)
        await state.set_state(MentorForm.description)
        await message.answer("Напишите описание для вашей анкеты:")
    except:
        await message.answer("Пожалуйста, введите корректный процент (число от 1 до 100)!")

@router.message(MentorForm.description)
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()
    
    with Session() as session:
        mentor = session.query(Mentor).filter_by(user_id=message.from_user.id).first()
        if not mentor:
            mentor = Mentor(user_id=message.from_user.id)
            session.add(mentor)
        
        mentor.direction = data['direction']
        mentor.commission = data['commission']
        mentor.description = message.text
        session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Анкета наставника успешно сохранена!",
        reply_markup=main_menu_kb(message.from_user.id)
    )