
import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, AudioPiped
from pytgcalls.exceptions import GroupCallNotFoundError
from gtts import gTTS
import yt_dlp
import openai

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call = PyTgCalls(user)

os.makedirs("downloads", exist_ok=True)

async def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"downloads/{info['id']}.mp3", info.get('title', 'No Title')

async def speak(chat_id, text):
    tts = gTTS(text=text, lang='ar')
    file_path = "downloads/speak.mp3"
    tts.save(file_path)
    await call.join_group_call(
        chat_id,
        InputStream(AudioPiped(file_path)),
        stream_type="local_stream"
    )

async def get_ai_reply(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception:
        return "حدث خطأ أثناء الاتصال بالذكاء الصناعي."

@app.on_message(filters.command("play") & filters.group)
async def play(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("أرسل رابط بعد الأمر /play")
    url = msg.command[1]
    await msg.reply("يتم التحميل...")
    try:
        audio_file, title = await download_audio(url)
        await call.join_group_call(
            msg.chat.id,
            InputStream(AudioPiped(audio_file)),
            stream_type="local_stream"
        )
        await msg.reply(f"تم تشغيل: {title}")
    except GroupCallNotFoundError:
        await msg.reply("⚠️ يجب بدء مكالمة صوتية أولاً.")
    except Exception as e:
        await msg.reply(f"حدث خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, msg: Message):
    try:
        await call.leave_group_call(msg.chat.id)
        await msg.reply("⏹️ تم إيقاف الصوت.")
    except Exception:
        await msg.reply("⚠️ لم أتمكن من الخروج من المكالمة.")

@app.on_message(filters.new_chat_members)
async def welcome(_, msg: Message):
    for member in msg.new_chat_members:
        await speak(msg.chat.id, f"أهلاً {member.first_name} في المجموعة!")

@app.on_message(filters.text & filters.group)
async def ai_talk(_, msg: Message):
    if msg.text.startswith("/"): return
    await msg.reply("🔍 جاري التفكير...")
    answer = await get_ai_reply(msg.text)
    await speak(msg.chat.id, answer)
    await msg.reply(answer)

@call.on_stream_end()
async def on_end(_, update):
    await call.leave_group_call(update.chat_id)

async def main():
    await app.start()
    await user.start()
    await call.start()
    print("✅ البوت يعمل الآن.")
    await idle()
    await app.stop()
    await user.stop()

if __name__ == "__main__":
    asyncio.run(main())
