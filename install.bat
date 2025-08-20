@echo off
echo Установка зависимостей для Spotify Telegram Bot...
echo.

echo Проверяем Python...
python --version
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден! Установите Python 3.8+ с python.org
    pause
    exit /b 1
)

echo.
echo Устанавливаем зависимости...
pip install -r requirements.txt

echo.
echo Создаем папку для загрузок...
if not exist "downloads" mkdir downloads

echo.
echo Установка завершена!
echo.
echo Следующие шаги:
echo 1. Отредактируйте config.py с вашими токенами
echo 2. Установите FFmpeg (https://ffmpeg.org/download.html)
echo 3. Запустите: python spotify_telegram_bot.py
echo.
pause