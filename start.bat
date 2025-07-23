@echo off
title Work Bot Auto-Reloader
color 0A
mode con:cols=80 lines=25

:check_python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не установлен или не добавлен в PATH
    echo Установите Python и добавьте его в переменные среды
    pause
    exit /b 1
)

:check_dependencies
pip show aiogram >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Aiogram не установлен
    echo Устанавливаю зависимости...
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось установить зависимости
        pause
        exit /b 1
    )
)

:start_bot
echo [%time%] Запускаем Work Bot...
echo ========================================
python bot/main.py

if %errorlevel% equ 0 (
    echo [%time%] Бот завершил работу корректно
    pause
    exit /b 0
)

echo [%time%] Бот упал с кодом ошибки %errorlevel%
echo Возможные причины:
echo 1. Проблемы с интернет-соединением
echo 2. Неверный токен бота
echo 3. Ошибки в коде
echo 4. Проблемы с базой данных
echo 5. Превышены лимиты Telegram API

echo Перезапуск через 5 секунд...
timeout /t 5 /nobreak >nul
echo ========================================
goto start_bot