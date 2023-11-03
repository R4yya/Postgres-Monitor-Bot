from dotenv import load_dotenv
import logging
import os
import psycopg2

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO

)

def connect_to_database():
    connection = psycopg2.connect(
        host=os.getenv('HOST'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD')
    )
    return connection

def get_database_list():
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        cursor.execute("SELECT datname FROM pg_database;")
        result = cursor.fetchall()

        if result:
            database_list = [row[0] for row in result]
            return database_list
        else:
            return []

    except Exception as e:
        return str(e)
    finally:
        if connection:
            connection.close()

def get_active_sessions_count(database_name):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        query = f"SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '{database_name}';"
        cursor.execute(query)

        result = cursor.fetchone()

        if result:
            active_sessions_count = result[0]
            return active_sessions_count
        else:
            return 0

    except Exception as e:
        return str(e)
    finally:
        if connection:
            connection.close()

def select_metric_keyboard():
    keyboard = [
        [InlineKeyboardButton("Active Sessions", callback_data="select_metric:active_sessions")]
    ]

    return InlineKeyboardMarkup(keyboard)

def select_database_buttons():
    database_list = get_database_list()
    buttons = []

    for database in database_list:
        button = InlineKeyboardButton(database, callback_data=f"select_db:{database}")
        buttons.append([button])

    return InlineKeyboardMarkup(buttons)

def go_back_button():
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="go_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def monitor(update: Update, context: CallbackContext):
    context.user_data['selected_metric'] = None
    await update.message.reply_text("Select a metric to view:", reply_markup=select_metric_keyboard())

    return SELECT_METRIC

async def select_database_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    selected_metric = query.data.split(":")[1]

    if selected_metric == "active_sessions":
        context.user_data['selected_metric'] = selected_metric
        context.user_data['selected_database'] = None

        keyboard = InlineKeyboardMarkup([
            [select_database_buttons()],
            [go_back_button()]
        ])

        await query.message.edit_text(
            text="Select a database to view active sessions:",
            reply_markup=keyboard
        )

        return SELECT_DATABASE

    return ConversationHandler.END

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    selected_data = query.data

    if selected_data == "go_back":
        await query.message.edit_text("Select a metric to view:", reply_markup=select_metric_keyboard())
        return SELECT_METRIC

    selected_database = selected_data.split(":")[1]

    if context.user_data['selected_metric'] == "active_sessions":
        context.user_data['selected_database'] = selected_database

        active_sessions_count = get_active_sessions_count(selected_database)
        message = f"Active sessions in {selected_database}: {active_sessions_count}"

        await query.message.edit_text(message, reply_markup=go_back_button())

    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('API_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    SELECT_METRIC, SELECT_DATABASE = range(2)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('monitor', monitor)],
        states={
            SELECT_METRIC: [CallbackQueryHandler(select_database_button)],
            SELECT_DATABASE: [CallbackQueryHandler(button)]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    application.run_polling()
