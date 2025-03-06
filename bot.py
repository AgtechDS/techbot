from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os

# Token del bot e ID gruppi/canali Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
QUOTE_CHANNEL_ID = "-1002290498999"  # Canale per preventivi
SUPPORT_GROUP_ID = "-2352452423"  # **Sostituisci con l'ID corretto del gruppo di assistenza**

# Funzione per ottenere l'ID di un gruppo
async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"🆔 ID di questo gruppo: `{chat_id}`")

# Funzione per creare la tastiera iniziale
def start_keyboard():
    keyboard = [
        [InlineKeyboardButton("Sito Web 🌐", url="https://agtechwebsite.vercel.app")],
        [InlineKeyboardButton("Prodotti 📦", callback_data='prodotti')],
        [InlineKeyboardButton("Assistenza 🆘", callback_data='assistenza')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Funzione per il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenuto! Come posso aiutarti oggi?",
        reply_markup=start_keyboard()
    )

# Funzione per gestire i pulsanti
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'prodotti':
        await send_product_categories(query)
    elif query.data == 'assistenza':
        await query.message.reply_text("✉️ Invia il tuo messaggio di assistenza. Verrà registrato come ticket.")
        context.user_data['waiting_for_assistance'] = True
    elif query.data.startswith("category_"):
        category = query.data.split("_")[1]
        await send_products_by_category(query, category)
    elif query.data.startswith("quote_"):
        product_name = query.data.split("_")[1]
        await request_quote(query, context, product_name)

# Funzione per mostrare le categorie di prodotti
async def send_product_categories(query):
    keyboard = [
        [InlineKeyboardButton("Excel Board & File 📊", callback_data="category_excel")],
        [InlineKeyboardButton("Custom Software 💻", callback_data="category_software")],
        [InlineKeyboardButton("AI Agent 🤖", callback_data="category_ai")],
        [InlineKeyboardButton("🔙 Indietro", callback_data="start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📦 **Seleziona una categoria di prodotti:**", reply_markup=reply_markup)

# Funzione per mostrare i prodotti di una categoria
async def send_products_by_category(query, category):
    products = {
        "excel": [
            ("Dashboard Finance", "Report finanziari automatici.", "quote_dashboard"),
            ("Gestione Magazzino", "Traccia e organizza il magazzino.", "quote_magazzino")
        ],
        "software": [
            ("Gestionale Aziendale", "Software su misura per la tua azienda.", "quote_gestionale"),
            ("App Mobile", "Sviluppo app per iOS e Android.", "quote_app")
        ],
        "ai": [
            ("Chatbot AI", "Assistenti virtuali personalizzati.", "quote_chatbot"),
            ("Analisi Dati AI", "Modelli AI per analisi avanzate.", "quote_analisi")
        ]
    }

    keyboard = []
    for name, description, callback in products.get(category, []):
        keyboard.append([InlineKeyboardButton(f"{name} - {description}", callback_data=callback)])

    keyboard.append([InlineKeyboardButton("🔙 Indietro", callback_data="prodotti")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(f"🛒 **Prodotti disponibili per {category.capitalize()}**", reply_markup=reply_markup)

# Funzione per richiedere un preventivo
async def request_quote(query, context, product_name):
    user = query.from_user
    message = f"📌 **Nuova Richiesta di Preventivo**\n🛒 **Prodotto:** {product_name}\n👤 **Utente:** @{user.username or 'Sconosciuto'} ({user.id})"

    await query.message.reply_text(f"📩 Hai richiesto un preventivo per **{product_name}**. Ti contatteremo al più presto!")
    await context.bot.send_message(QUOTE_CHANNEL_ID, message)

# Funzione per gestire i messaggi di assistenza
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_assistance', False):
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "Sconosciuto"
        message_text = update.message.text

        ticket_id = save_ticket(user_id, message_text)

        response = f"✅ **Ticket #{ticket_id} aperto!** Ti risponderemo al più presto."
        await update.message.reply_text(response)

        # Invia il messaggio al gruppo di assistenza
        admin_message = (
            f"📩 **Nuova Richiesta di Assistenza!**\n"
            f"🎫 **Ticket ID:** {ticket_id}\n"
            f"👤 **Utente:** @{username} ({user_id})\n"
            f"📝 **Messaggio:** {message_text}"
        )
        # Debug: Verifica invio al gruppo
        print(f"Invio messaggio al gruppo {SUPPORT_GROUP_ID}")
        try:
            await context.bot.send_message(SUPPORT_GROUP_ID, admin_message)
            print("✅ Messaggio inviato con successo!")
        except Exception as e:
            print(f"❌ Errore nell'invio del messaggio: {e}")

        # Reset dello stato
        context.user_data['waiting_for_assistance'] = False
    else:
        await update.message.reply_text("❓ Usa la tastiera per navigare tra le opzioni disponibili.")

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

# Funzione principale
def main():
    setup_database()

    app = Application.builder().token(BOT_TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getgroupid", get_group_id))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
