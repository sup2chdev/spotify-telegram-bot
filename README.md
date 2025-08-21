# Spotify Telegram Bot

Telegram бот для скачивания музыки из Spotify плейлистов и отдельных треков.
*если вы в рф то при запуске в powershell впишите https прокси, их можно купить за пару медяков либо вообще найти бесплатно, как подключить? Вы не маленькие в интернете легко найдете ( или у чатагпт спросите XD )*

## Возможности

- 🎵 Скачивание отдельных треков по Spotify ссылке
- 📋 Скачивание целых плейлистов из Spotify
- 🔍 Поиск и скачивание по названию трека
- 📁 Отправка файлов в формате MP3 прямо в чат

## Установка

1. Установите Python 3.8+
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите FFmpeg (необходим для конвертации аудио):
   - Windows: Скачайте с https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

## Настройка

1. Создайте Telegram бота:
   - Напишите @BotFather в Telegram
   - Создайте нового бота командой `/newbot`
   - Скопируйте токен бота

2. Получите Spotify API ключи:
   - Зайдите на https://developer.spotify.com/
   - Создайте новое приложение
   - Скопируйте Client ID и Client Secret

3. Скопируйте файл конфигурации и заполните его:
```bash
cp config.example.py config.py
```

4. Отредактируйте файл `config.py`:
```python
TELEGRAM_BOT_TOKEN = "ваш_токен_бота"
SPOTIFY_CLIENT_ID = "ваш_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "ваш_spotify_client_secret"
```

## Запуск

```bash
python spotify_telegram_bot.py
```

## Использование

1. Запустите бота командой `/start`
2. Отправьте боту:
   - Ссылку на Spotify трек: `https://open.spotify.com/track/...`
   - Ссылку на Spotify плейлист: `https://open.spotify.com/playlist/...`
   - Название трека для поиска: `Imagine Dragons - Believer`

Бот найдет трек на YouTube, скачает его и отправит вам MP3 файл.

## Примеры ссылок

- Трек: `https://open.spotify.com/track/0VjIjW4GlULA7QiSV6Fdn9`
- Плейлист: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`

## Требования

- Python 3.8+
- FFmpeg
- Интернет соединение
- Telegram Bot Token
- Spotify API ключи

## Примечания

- Бот скачивает музыку с YouTube, используя информацию из Spotify
- Качество аудио: 192 kbps MP3
- Файлы автоматически удаляются после отправки
- Поддерживается только публичные Spotify плейлисты
