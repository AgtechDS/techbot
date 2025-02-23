from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os

# Token del bot (usa le variabili d'ambiente su Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Funzione per creare la pulsantiera base
def start_keyboard():
    keyboard = [
        [InlineKeyboardButton("Sito Web 🌍", url="https://agtechwebsite.vercel.app")],
        [InlineKeyboardButton("Prodotti 🛒", callback_data='prodotti')],
        [InlineKeyboardButton("Assistenza 🆘", callback_data='assistenza')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Funzione per gestire il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Benvenuto nel bot di **AgTechDesigne**! Seleziona un'opzione dal menu:",
        reply_markup=start_keyboard()
    )

# Funzione per gestire i tasti "Prodotti" e "Assistenza"
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'prodotti':
        await send_product_categories(query)
    elif query.data == 'assistenza':
        await query.message.reply_text("✍️ Scrivi il tuo messaggio di assistenza, verrà inviato come ticket.")
        context.user_data['waiting_for_assistance'] = True
    elif query.data.startswith("category_"):
        category = query.data.split("_")[1]
        await send_products(query, category)
    elif query.data.startswith("request_"):
        product_name = query.data.split("_", 1)[1]
        await request_quote(query, product_name)

# Funzione per mostrare le categorie di prodotti
async def send_product_categories(query):
    keyboard = [
        [InlineKeyboardButton("📊 Excel Board and File", callback_data='category_excel')],
        [InlineKeyboardButton("💻 Custom Software", callback_data='category_software')],
        [InlineKeyboardButton("🤖 AI Agent", callback_data='category_ai')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("📦 **Seleziona una categoria di prodotti:**", reply_markup=reply_markup)

# Funzione per mostrare i prodotti in una categoria
async def send_products(query, category):
    products = {
        "excel": [
            ("Dashboard Interattiva", "📊 Report automatizzati e interattivi in Excel."),
            ("Gestione Inventario", "📦 Foglio Excel avanzato per il controllo delle scorte.")
        ],
        "software": [
            ("Software Gestionale", "💼 Applicazione personalizzata per la tua azienda."),
            ("Automazione Dati", "🔄 Automazione di processi ripetitivi con software su misura.")
        ],
        "ai": [
            ("AI Chatbot", "🤖 Bot intelligente per supporto clienti e automazione."),
            ("Analisi Predittiva", "📈 AI per previsioni basate su dati e analisi avanzate.")
        ]
    }

    if category not in products:
        await query.message.reply_text("❌ Categoria non trovata.")
        return

    keyboard = []
    for name, desc in products[category]:
        keyboard.append([InlineKeyboardButton(f"{name}", callback_data=f"request_{name.replace(' ', '_')}")])
        await query.message.reply_text(f"**{name}**\n{desc}")

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("💡 **Seleziona un prodotto per richiedere un preventivo:**", reply_markup=reply_markup)

# Funzione per richiedere un preventivo
async def request_quote(query, product_name):
    product_name = product_name.replace("_", " ")
    await query.message.reply_text(f"📩 Hai richiesto un preventivo per **{product_name}**.\nIl nostro team ti contatterà presto!")
    
    # Notifica all'admin con il prodotto richiesto
    await query.bot.send_message(ADMIN_ID, f"📌 **Nuova richiesta di preventivo:**\n🛒 **Prodotto:** {product_name}\n📩 Contatta l'utente!")

# Funzione per gestire i messaggi (assistenza)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'waiting_for_assistance' in context.user_data and context.user_data['waiting_for_assistance']:
        user_id = update.message.from_user.id
        message_text = update.message.text

        ticket_id = save_ticket(user_id, message_text)
        await update.message.reply_text(f"✅ **Ticket #{ticket_id} aperto!** Ti risponderemo al più presto.")

        await context.bot.send_message(ADMIN_ID, f"📩 **Nuovo ticket di assistenza!**\n🎫 **Ticket #{ticket_id}**\n💬 Messaggio: {message_text}")

        context.user_data['waiting_for_assistance'] = False
    else:
        await update.message.reply_text("❓ Usa il menu per navigare tra le opzioni.")

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
    
    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot