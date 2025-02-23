from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Token del bot (inserisci il tuo)
BOT_TOKEN = "7318846050:AAHrfDFk4HrEUApNqs0Yxx84YWjIboDs3zo"

# Dizionario per memorizzare i ticket di assistenza
support_tickets = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di benvenuto con menu di opzioni"""
    keyboard = [
        [InlineKeyboardButton("💬 Richiedi Assistenza", callback_data="assist")],
        [InlineKeyboardButton("ℹ️ Info Servizi", callback_data="info")],
        [InlineKeyboardButton("📞 Contatti", callback_data="contatti")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Benvenuto su AgTechDesigne! Seleziona un'opzione:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte ai pulsanti del menu"""
    query = update.callback_query
    await query.answer()

    if query.data == "assist":
        await query.message.reply_text("📩 Invia il tuo messaggio di assistenza e ti risponderemo al più presto!")
        return
    elif query.data == "info":
        await query.message.reply_text("ℹ️ **Servizi Offerti:**\n- Sviluppo Software\n- Siti Web\n- AI Assistants\n- Automazione e Bot\n🔗 Maggiori info su: www.agtechdesigne.com")
    elif query.data == "contatti":
        await query.message.reply_text("📞 **Contatti**\n✉️ Email: agtechdesigne@gmail.com\n📷 Instagram: @agtechdesigne")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi degli utenti e crea un ticket di supporto"""
    user_id = update.message.from_user.id
    message_text = update.message.text
    ticket_id = len(support_tickets) + 1  # Genera un ID progressivo

    support_tickets[ticket_id] = {"user_id": user_id, "message": message_text}

    await update.message.reply_text(f"✅ **Ticket #{ticket_id} aperto!**\nTi risponderemo al più presto.")
    
    # Notifica all'admin (puoi inserire il tuo ID Telegram per ricevere le richieste)
    ADMIN_ID = "TUO_TELEGRAM_ID"
    await context.bot.send_message(ADMIN_ID, f"📩 **Nuova richiesta di assistenza!**\nTicket #{ticket_id}\nMessaggio: {message_text}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce gli errori"""
    print(f"Errore: {context.error}")

# Creazione e avvio del bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error Handler
    app.add_error_handler(error_handler)

    print("🤖 Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
