from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os
import pandas as pd

# Token del bot (usa le variabili d'ambiente su Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Funzione per creare la pulsantiera base
def start_keyboard():
    keyboard = [
        [InlineKeyboardButton("Sito Web", url="https://agtechwebsite.vercel.app")],
        [InlineKeyboardButton("Prodotti", callback_data='prodotti')],
        [InlineKeyboardButton("Assistenza", callback_data='assistenza')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Funzione per gestire il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenuto! Come posso aiutarti oggi?",
        reply_markup=start_keyboard()
    )

# Funzione per gestire i tasti "Prodotti" e "Assistenza"
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'prodotti':
        # Aggiungi i prodotti dal file Excel (esempio)
        await send_products(update)
    elif query.data == 'assistenza':
        # Inizia la raccolta del messaggio di assistenza
        await update.message.reply_text("Scrivi il tuo messaggio di assistenza, e verrà inviato come ticket.")
        return

# Funzione per inviare i prodotti dal file Excel
async def send_products(update: Update):
    # Carica il file Excel (assumendo che contenga una lista di prodotti)
    df = pd.read_excel('prodotti.xlsx')  # Assicurati di avere questo file nella cartella corretta
    product_list = df.to_string(index=False)

    # Invia i prodotti all'utente
    await update.message.reply_text(f"🛒 Ecco i nostri prodotti:\n\n{product_list}\n\nPer ulteriori dettagli, contattaci!")

# Funzione per gestire i messaggi di assistenza
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text

    # Crea un ticket per l'assistenza
    ticket_id = save_ticket(user_id, message_text)
    await update.message.reply_text(f"✅ **Ticket #{ticket_id} aperto!** Ti risponderemo al più presto.")

    # Notifica all'admin tramite il canale di Telegram
    await context.bot.send_message(ADMIN_ID, f"📩 **Nuova richiesta di assistenza!**\nTicket #{ticket_id}\nMessaggio: {message_text}")

# Funzione per salvare un ticket nel database
def save_ticket(user_id, message):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (user_id, message) VALUES (?, ?)", (user_id, message))
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
            status TEXT DEFAULT 'aperto'
        )
    """)
    conn.commit()
    conn.close()

# Funzione di avvio del bot
def main():
    setup_database()  # Crea il database se non esiste
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
