from enum import Enum

class UserRole(str, Enum):
    PENDING = "На рассмотрении"
    WORKER = "Воркер"
    MENTOR = "Наставник"
    ADMIN = "Администратор"
    OWNER = "Владелец"
    REJECTED = "Отклонен"