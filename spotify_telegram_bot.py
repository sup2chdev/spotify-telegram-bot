import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import requests
from urllib.parse import urlparse

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт конфигурации
try:
    from config import TELEGRAM_BOT_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
except ImportError:
    # Fallback значения
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_SPOTIFY_CLIENT_SECRET")

# Инициализация Spotify API
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

class MusicDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
    def search_youtube(self, query):
        """Поиск трека на YouTube"""
        search_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            try:
                search_results = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=False
                )
                if search_results and 'entries' in search_results and search_results['entries']:
                    return search_results['entries'][0]['webpage_url']
            except Exception as e:
                logger.error(f"Ошибка поиска на YouTube: {e}")
        return None
    
    def download_audio(self, url, title):
        """Скачивание аудио с YouTube"""
        try:
            # Создаем папку для загрузок
            os.makedirs('downloads', exist_ok=True)
            
            # Настройки для конкретного файла
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = f'downloads/{title}.%(ext)s'
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                return f'downloads/{title}.mp3'
        except Exception as e:
            logger.error(f"Ошибка скачивания: {e}")
            return None

downloader = MusicDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "Привет! Отправь мне ссылку на трек или плейлист Spotify, и я скачаю музыку для тебя!\n\n"
        "Поддерживаемые форматы:\n"
        "- Ссылка на трек Spotify\n"
        "- Ссылка на плейлист Spotify\n"
        "- Название трека для поиска"
    )

def get_spotify_track_info(track_id):
    """Получение информации о треке из Spotify"""
    try:
        track = spotify.track(track_id)
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'query': f"{track['artists'][0]['name']} - {track['name']}"
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о треке: {e}")
        return None

def get_spotify_playlist_tracks(playlist_id):
    """Получение треков из плейлиста Spotify"""
    try:
        results = spotify.playlist_tracks(playlist_id)
        tracks = []
        
        for item in results['items']:
            if item['track']:
                track = item['track']
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'query': f"{track['artists'][0]['name']} - {track['name']}"
                })
        
        return tracks
    except Exception as e:
        logger.error(f"Ошибка получения плейлиста: {e}")
        return []

def parse_spotify_url(url):
    """Парсинг Spotify URL"""
    try:
        if 'open.spotify.com' in url:
            parts = url.split('/')
            if 'track' in parts:
                track_id = parts[-1].split('?')[0]
                return 'track', track_id
            elif 'playlist' in parts:
                playlist_id = parts[-1].split('?')[0]
                return 'playlist', playlist_id
    except Exception as e:
        logger.error(f"Ошибка парсинга URL: {e}")
    return None, None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений"""
    message_text = update.message.text
    
    # Проверяем, является ли сообщение Spotify URL
    url_type, spotify_id = parse_spotify_url(message_text)
    
    if url_type == 'track':
        await download_single_track(update, spotify_id)
    elif url_type == 'playlist':
        await download_playlist(update, spotify_id)
    else:
        # Поиск по названию
        await search_and_download(update, message_text)

async def download_single_track(update: Update, track_id):
    """Скачивание одного трека"""
    await update.message.reply_text("🔍 Получаю информацию о треке...")
    
    track_info = get_spotify_track_info(track_id)
    if not track_info:
        await update.message.reply_text("❌ Не удалось получить информацию о треке")
        return
    
    await update.message.reply_text(f"🎵 Скачиваю: {track_info['query']}")
    
    # Поиск на YouTube
    youtube_url = downloader.search_youtube(track_info['query'])
    if not youtube_url:
        await update.message.reply_text("❌ Трек не найден на YouTube")
        return
    
    # Скачивание
    file_path = downloader.download_audio(youtube_url, track_info['name'])
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio_file,
                    title=track_info['name'],
                    performer=track_info['artist']
                )
            # Удаляем файл после отправки
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка отправки файла: {e}")
    else:
        await update.message.reply_text("❌ Не удалось скачать трек")

async def download_playlist(update: Update, playlist_id):
    """Скачивание плейлиста"""
    await update.message.reply_text("🔍 Получаю треки из плейлиста...")
    
    tracks = get_spotify_playlist_tracks(playlist_id)
    if not tracks:
        await update.message.reply_text("❌ Не удалось получить треки из плейлиста")
        return
    
    await update.message.reply_text(f"📋 Найдено {len(tracks)} треков. Начинаю скачивание...")
    
    for i, track in enumerate(tracks, 1):
        try:
            await update.message.reply_text(f"🎵 ({i}/{len(tracks)}) {track['query']}")
            
            # Поиск на YouTube
            youtube_url = downloader.search_youtube(track['query'])
            if not youtube_url:
                await update.message.reply_text(f"❌ Трек {track['name']} не найден")
                continue
            
            # Скачивание
            file_path = downloader.download_audio(youtube_url, track['name'])
            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio_file,
                        title=track['name'],
                        performer=track['artist']
                    )
                os.remove(file_path)
            else:
                await update.message.reply_text(f"❌ Не удалось скачать {track['name']}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка с треком {track['name']}: {e}")
    
    await update.message.reply_text("✅ Плейлист обработан!")

async def search_and_download(update: Update, query):
    """Поиск и скачивание по запросу"""
    await update.message.reply_text(f"🔍 Ищу: {query}")
    
    # Поиск на YouTube
    youtube_url = downloader.search_youtube(query)
    if not youtube_url:
        await update.message.reply_text("❌ Трек не найден")
        return
    
    # Скачивание
    safe_filename = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
    file_path = downloader.download_audio(youtube_url, safe_filename)
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_audio(audio_file, title=query)
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка отправки: {e}")
    else:
        await update.message.reply_text("❌ Не удалось скачать трек")

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()