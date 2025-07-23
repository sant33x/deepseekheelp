from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Any, Dict

from bot.database.models import get_session, User
from bot.utils.roles import UserRole
from bot.utils.config import Config

class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Исключения для публичных команд
        if event.text and event.text.startswith(('/start', '/help')):
            return await handler(event, data)
            
        # Проверка доступа
        with get_session() as session:
            user = session.query(User).filter_by(user_id=event.from_user.id).first()
            if not user or user.status not in [UserRole.WORKER, UserRole.MENTOR, UserRole.ADMIN]:
                await event.answer(
                    "❌ Доступ ограничен\n\n"
                    "Для получения доступа к боту пройдите регистрацию через /start"
                )
                return
        
        return await handler(event, data)