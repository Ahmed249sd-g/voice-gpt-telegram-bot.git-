
import os, sys
from pyrogram import Client
from pyrogram.sessions import StringSession

def prompt_env(var):
    val = input(f"{var}: ").strip()
    if not val:
        print(f"{var} لا يمكن أن يكون فارغًا.")
        sys.exit(1)
    return val

def main():
    print("أدخل بيانات Telegram و OpenAI:")
    api_id = prompt_env("API_ID")
    api_hash = prompt_env("API_HASH")
    bot_token = prompt_env("BOT_TOKEN")
    openai_key = prompt_env("OPENAI_API_KEY")

    app = Client(":session", api_id=int(api_id), api_hash=api_hash)
    app.start()
    session = app.export_session_string()
    app.stop()

    with open(".env", "w") as f:
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
        f.write(f"BOT_TOKEN={bot_token}\n")
        f.write(f"SESSION_STRING={session}\n")
        f.write(f"OPENAI_API_KEY={openai_key}\n")

    print("✅ تم إنشاء ملف .env")

if __name__ == "__main__":
    main()
