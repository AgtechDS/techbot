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
        await send_product_categories(query)
    elif query.data.startswith('category_'):
        category = query.data.split('_')[1]
        await send_products(query, category)
    elif query.data.startswith('preventivo_'):
        product_name = query.data.split('_')[1]
        await request_quote(query, product_name)
    elif query.data == 'assistenza':
        await query.message.reply_text("Scrivi il tuo messaggio di assistenza, e verrà inviato come ticket.")
        context.user_data['waiting_for_assistance'] = True

# Funzione per inviare le categorie di prodotti
async def send_product_categories(update: Update):
    keyboard = [
        [InlineKeyboardButton("Excel Board and File", callback_data='category_excel')],
        [InlineKeyboardButton("Custom Software", callback_data='category_software')],
        [InlineKeyboardButton("AI Agent", callback_data='category_ai')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("📦 **Seleziona una categoria di prodotti:**", reply_markup=reply_markup)

# Funzione per inviare i prodotti di una categoria specifica
async def send_products(update: Update, category: str):
    df = pd.read_excel('prodotti.xlsx')

    products = df[df['Categoria'] == category]

    if products.empty:
        await update.callback_query.message.reply_text("⚠️ Nessun prodotto disponibile in questa categoria.")
        return

    for _, row in products.iterrows():
        product_name = row["Nome"]
        description = row["Descrizione"]
        keyboard = [[InlineKeyboardButton("💬 Richiedi Preventivo", callback_data=f'preventivo_{product_name}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text(
            f"🔹 **{product_name}**\n{description}", 
            reply_markup=reply_markup
        )

# Funzione per gestire la richiesta di preventivo
async def request_quote(update: Update, product_name: str):
    user_id = update.callback_query.from_user.id
    ticket_id = save_ticket(user_id, f"Richiesta preventivo per {product_name}")

    await update.callback_query.message.reply_text(
        f"✅ **Richiesta inviata!**\nTicket #{ticket_id} per il prodotto: {product_name}"
    )

    await update.callback_query.message.reply_text(
        f"📩 **Nuova richiesta di preventivo!**\nTicket #{ticket_id}\nProdotto: {product_name}",
        chat_id=ADMIN_ID
    )

# Funzione per gestire i messaggi di assistenza
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'waiting_for_assistance' in context.user_data and context.user_data['waiting_for_assistance']:
        user_id = update.message.from_user.id
        message_text = update.message.text

        ticket_id = save_ticket(user_id, message_text)
        await update.message.reply_text(f"✅ **Ticket #{ticket_id} aperto!** Ti risponderemo al più presto.")

        await context.bot.send_message(ADMIN_ID, f"📩 **Nuova richiesta di assistenza!**\nTicket #{ticket_id}\nMessaggio: {message_text}")

        context.user_data['waiting_for_assistance'] = False
    else:
        await update.message.reply_text("Per favore, seleziona una delle opzioni dalla tastiera.")

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
    setup_database()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()