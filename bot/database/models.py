from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from bot.utils.config import Config

Base = declarative_base()
engine = create_engine(f"sqlite:///{Config.DB_PATH}")
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    status = Column(String, default="pending")
    custom_tag = Column(String)
    registration_date = Column(DateTime, default=datetime.now)
    mentor_id = Column(Integer, ForeignKey('mentors.id'), nullable=True)
    
    profits = relationship("Profit", back_populates="user")
    applications = relationship("Application", back_populates="user")
    mentor = relationship("Mentor", back_populates="users")

class Profit(Base):
    __tablename__ = 'profits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    direction = Column(String, nullable=False)
    service = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="profits")

class Mentor(Base):
    __tablename__ = 'mentors'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    direction = Column(String, nullable=False)
    commission = Column(Float, nullable=False)
    description = Column(String)
    
    users = relationship("User", back_populates="mentor")

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    answer1 = Column(String, nullable=False)
    answer2 = Column(String, nullable=False)
    answer3 = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="applications")

def create_tables():
    """Создает все таблицы в базе данных"""
    Base.metadata.create_all(engine)

def drop_tables():
    """Удаляет все таблицы (для тестов)"""
    Base.metadata.drop_all(engine)

def recreate_tables():
    """Пересоздает все таблицы"""
    drop_tables()
    create_tables()

def get_session():
    """Возвращает новую сессию для работы с БД"""
    return Session()