from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("7318846050:AAHrfDFk4HrEUApNqs0Yxx84YWjIboDs3zo")

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Chat ID: {chat_id}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("chatid", get_chat_id))
    print("🤖 Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
