from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import openai
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("🔑 TELEGRAM_BOT_TOKEN =", TELEGRAM_BOT_TOKEN)
print("🔑 OPENAI_API_KEY =", OPENAI_API_KEY[:10] + "..." if OPENAI_API_KEY else "None")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام سوال تو بپرس بدرد نخور")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # ✅ تایپ کردن قبل از تولید پاسخ
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # ✅ حافظه مکالمه
        if "history" not in context.chat_data:
            context.chat_data["history"] = []
        context.chat_data["history"].append({"role": "user", "content": user_message})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=context.chat_data["history"]
        )
        answer = response['choices'][0]['message']['content']
        context.chat_data["history"].append({"role": "assistant", "content": answer})

        await update.message.reply_text(answer)

        tts = gTTS(answer, lang='fa')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as audio:
            await update.message.reply_voice(audio)

    except Exception:
        pass  # ارورها کامل خاموش

if __name__ == '__main__':
    if TELEGRAM_BOT_TOKEN and OPENAI_API_KEY:
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("✅ ربات اجرا شد.")
        app.run_polling()
    else:
        print("❌ توکن‌ها به درستی لود نشدن. فایل .env رو بررسی کن.")
