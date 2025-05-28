import os
import asyncio
from fastapi import FastAPI
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from ffmpeg_hls import convert_to_hls

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))

app = FastAPI()
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_event("startup")
async def startup():
    await bot.start()

@app.on_event("shutdown")
async def shutdown():
    await bot.stop()

@bot.on_message(filters.document | filters.video)
async def handle_file(client, message: Message):
    file = message.document or message.video
    file_path = await message.download()
    file_id = str(message.id)
    out_dir = f"hls/{file_id}"
    convert_to_hls(file_path, out_dir)

    stream_link = f"https://your-koyeb-app.koyeb.app/player/{file_id}"
    download_link = f"https://your-koyeb-app.koyeb.app/download/{file_id}"

    await message.reply_text(
        f"✅ **File Processed**

"
        f"📥 **Download:** {download_link}
"
        f"▶️ **Stream:** {stream_link}"
    )

    await client.send_message(
        LOG_CHANNEL,
        f"#NEW_UPLOAD

File ID: `{file_id}`
User: {message.from_user.mention}
Stream: {stream_link}"
    )

@app.get("/player/{file_id}")
async def player(file_id: str):
    with open("templates/player.html", "r") as f:
        content = f.read().replace("{{FILE_ID}}", file_id)
    return content

@app.get("/download/{file_id}")
async def download_link(file_id: str):
    return {"url": f"/hls/{file_id}/stream_0.m3u8"}
