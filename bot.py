from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3  # Per il database
import os

# Token del bot (usa le variabili d'ambiente su Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Dizionario di FAQ
FAQ = {
    "costi": "💰 I costi dipendono dal progetto. Contattaci per un preventivo gratuito!",
    "tempi di sviluppo": "⏳ Il tempo varia in base alla complessità. Di solito, da 1 a 4 settimane.",
    "ai assistenti": "🤖 Creiamo AI personalizzati per automazione, chat e assistenza.",
    "siti web": "🖥️ Realizziamo siti web moderni, sia vetrina che e-commerce."
}

# Funzione per rispondere alle FAQ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text.lower()

    # Controlla se il messaggio corrisponde a una FAQ
    for keyword, response in FAQ.items():
        if keyword in message_text:
            await update.message.reply_text(response)
            return

    # Se non è una FAQ, crea un ticket
    ticket_id = save_ticket(user_id, message_text, "aperto")
    await update.message.reply_text(f"✅ **Ticket #{ticket_id} aperto!**\nTi risponderemo al più presto.")
    
    # Notifica all'admin
    await context.bot.send_message(ADMIN_ID, f"📩 **Nuova richiesta di assistenza!**\nTicket #{ticket_id}\nMessaggio: {message_text}")

# Funzione per salvare un ticket nel database
def save_ticket(user_id, message, status):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (user_id, message, status) VALUES (?, ?, ?)", (user_id, message, status))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

# Funzione per creare il database
def setup_database():
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            status TEXT DEFAULT 'aperto',
            priority TEXT DEFAULT 'media'
        )
    """)
    conn.commit()
    conn.close()

# Funzione di avvio del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia un messaggio di benvenuto al comando /start"""
    keyboard = [
        [InlineKeyboardButton("FAQ", callback_data='faq')],
        [InlineKeyboardButton("Assistenza tecnica", callback_data='assistente')],
        [InlineKeyboardButton("Richiesta personalizzata", callback_data='richiesta')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ciao! Sono il bot di assistenza tecnica di AgTechDesigne. Come posso aiutarti?", reply_markup=reply_markup)

# Funzione per gestire i bottoni
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "faq":
        await query.edit_message_text(text="Ecco alcune FAQ:\n\n1. Costi\n2. Tempi di sviluppo\n3. AI Assistenti\n4. Siti web")
    elif data == "assistente":
        await query.edit_message_text(text="Puoi inviare il tuo messaggio e aprire un ticket. Ti risponderemo al più presto.")
    elif data == "richiesta":
        await query.edit_message_text(text="Compila il modulo per richiedere una consulenza personalizzata.")

# Funzione per gestire il comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia il comando di aiuto"""
    await update.message.reply_text("Benvenuto! Usa i seguenti comandi:\n\n/start - Avvia il bot\n/help - Mostra aiuto\n/faq - Consulta le FAQ")

# Funzione principale
def main():
    setup_database()  # Crea il database se non esiste
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Aggiungi gestori per i comandi e i messaggi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
