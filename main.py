import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv("config.env")

API_ID = int(os.getenv("API_ID", "12345"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-100xxxxxxxxxx"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h1>Telegram Streaming Bot is Running</h1>"

@app.get("/player/{file_id}", response_class=HTMLResponse)
async def stream_video(file_id: str):
    return open("templates/player.html", "r").read().replace("{{ file_id }}", file_id)

@app.get("/video/{file_id}/{quality}", response_class=FileResponse)
async def serve_video(file_id: str, quality: str):
    return FileResponse(f"downloads/{file_id}/{quality}.m3u8")

@app.get("/download/{file_id}", response_class=FileResponse)
async def download_file(file_id: str):
    return FileResponse(f"downloads/{file_id}/original.mp4")

@bot.on_message(filters.private & (filters.video | filters.document))
async def handle_file(client: Client, message: Message):
    file_name = message.document.file_name if message.document else message.video.file_name
    file_id = str(message.id)
    download_path = f"downloads/{file_id}/original.mp4"
    os.makedirs(f"downloads/{file_id}", exist_ok=True)
    await message.download(file_name=download_path)

    os.system(f"ffmpeg -i {download_path} -filter:v scale=-2:144 -c:a copy downloads/{file_id}/144p.m3u8")
    os.system(f"ffmpeg -i {download_path} -filter:v scale=-2:240 -c:a copy downloads/{file_id}/240p.m3u8")
    os.system(f"ffmpeg -i {download_path} -filter:v scale=-2:360 -c:a copy downloads/{file_id}/360p.m3u8")
    os.system(f"ffmpeg -i {download_path} -filter:v scale=-2:480 -c:a copy downloads/{file_id}/480p.m3u8")
    os.system(f"ffmpeg -i {download_path} -filter:v scale=-2:720 -c:a copy downloads/{file_id}/720p.m3u8")
    os.system(f"ffmpeg -i {download_path} -filter:v scale=-2:1080 -c:a copy downloads/{file_id}/1080p.m3u8")

    stream_link = f"{BASE_URL}/player/{file_id}"
    download_link = f"{BASE_URL}/download/{file_id}"

    await message.reply_text(
        f"✅ File processed!\n▶️ Stream: {stream_link}\n📥 Download: {download_link}"
    )
    await bot.send_message(
        LOG_CHANNEL,
        f"✅ **File Processed**\n📁 Name: {file_name}\n🆔 ID: {file_id}\n📥 [Download Link]({download_link})\n▶️ [Stream Link]({stream_link})"
    )

def start():
    bot.start()
    loop = asyncio.get_event_loop()
    loop.create_task(app.run())

if __name__ == "__main__":
    start()
