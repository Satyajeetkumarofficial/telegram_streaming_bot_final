import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import uvicorn

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
    download_folder = f"downloads/{file_id}"
    download_path = f"{download_folder}/original.mp4"
    os.makedirs(download_folder, exist_ok=True)
    await message.download(file_name=download_path)

    # HLS multiple quality transcoding
    qualities = [144, 240, 360, 480, 720, 1080]
    for q in qualities:
        os.system(f"ffmpeg -i {download_path} -vf scale=-2:{q} -c:a aac -c:v h264 -f hls -hls_time 10 -hls_playlist_type vod {download_folder}/{q}p.m3u8")

    stream_link = f"{BASE_URL}/player/{file_id}"
    download_link = f"{BASE_URL}/download/{file_id}"

    await message.reply_text(
        f"✅ File processed!\n▶️ Stream: {stream_link}\n📥 Download: {download_link}"
    )
    await bot.send_message(
        LOG_CHANNEL,
        f"✅ **File Processed**\n📁 Name: {file_name}\n🆔 ID: {file_id}\n📥 [Download Link]({download_link})\n▶️ [Stream Link]({stream_link})"
    )

async def start_bot():
    await bot.start()
    print("Bot started")

async def main():
    await start_bot()
    config = uvicorn.Config(app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
