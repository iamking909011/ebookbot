from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import asyncio
import threading

# === Telegram Bot Config ===
BOT_TOKEN = '7459877430:AAG4yG0f_uzdb19J6J8rK2k9DCphCm7PH8I'
CHANNEL_USERNAME = '@CLASS11EBOOK'
SECRET_CODE = 'dream2025'
APK_LINK = 'https://asmultiverse.com/'

user_states = {}
user_messages = {}

# === Telegram Bot Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = 'awaiting_code'
    user_messages[user_id] = [update.message.message_id]

    keyboard = [[InlineKeyboardButton("📲 Visit Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await update.message.reply_text(
        "**Welcome to Your Dream Bot!** 🌟\n\nTo get the download link:\n"
        "1️⃣ Visit the channel\n"
        "2️⃣ Find the **secret code** (pinned)\n"
        "3️⃣ Send it here to unlock 🔓",
        reply_markup=reply_markup
    )
    user_messages[user_id].append(msg.message_id)

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg_text = update.message.text.strip()
    user_messages.setdefault(user_id, []).append(update.message.message_id)

    if user_states.get(user_id) == 'awaiting_code':
        if msg_text.lower() == SECRET_CODE.lower():
            for msg_id in user_messages[user_id]:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
                except:
                    pass
            await asyncio.sleep(0.3)
            await update.message.reply_text(f"✅ Correct code!\n\n🔗 Here is your download link:\n{APK_LINK}")
            user_states[user_id] = 'done'
            user_messages[user_id] = []
        else:
            error_msg = await update.message.reply_text("❌ Wrong code. Try again.")
            user_messages[user_id].append(error_msg.message_id)

# === Flask Keep-Alive Server ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Start Bot + Server Together ===
def main():
    threading.Thread(target=run_flask).start()
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    print("✅ Bot is running...")
    app_telegram.run_polling()

if __name__ == '__main__':
    main()
