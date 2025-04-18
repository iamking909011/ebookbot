from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
from threading import Thread
import asyncio

# === CONFIGURATION ===
BOT_TOKEN = '7459877430:AAG4yG0f_uzdb19J6J8rK2k9DCphCm7PH8I'
CHANNEL_USERNAME = '@CLASS11EBOOK'
SECRET_CODE = 'dream2025'
APK_LINK = 'https://asmultiverse.com/'

# === MEMORY ===
user_states = {}
user_messages = {}

# === TELEGRAM HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = 'awaiting_code'
    user_messages[user_id] = [update.message.message_id]

    keyboard = [
        [InlineKeyboardButton("📲 Visit Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await update.message.reply_text(
        "**Welcome to Your Dream Bot!** 🌟\n\nTo get the download link:\n"
        "1️⃣ Tap the button below to go to our channel\n"
        "2️⃣ Find the **secret code** (it's pinned!)\n"
        "3️⃣ Send it here to unlock the link 🔓",
        reply_markup=reply_markup
    )
    user_messages[user_id].append(msg.message_id)

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()
    user_messages.setdefault(user_id, []).append(update.message.message_id)

    if user_states.get(user_id) == 'awaiting_code':
        if text == SECRET_CODE.lower():
            for msg_id in user_messages[user_id]:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
                except:
                    pass
            await asyncio.sleep(0.5)
            await update.message.reply_text(f"✅ Correct code!\n\n🔗 Here is your download link:\n{APK_LINK}")
            user_states[user_id] = 'done'
            user_messages[user_id] = []
        else:
            msg = await update.message.reply_text("❌ Wrong code. Try again.")
            user_messages[user_id].append(msg.message_id)

# === FLASK KEEP-ALIVE ===
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "✅ Your Dream Bot is Alive!"

def run():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# === MAIN START ===
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    print("🤖 Bot is running...")
    app.run_polling()
