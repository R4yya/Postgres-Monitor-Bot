from dotenv import load_dotenv
import logging
import os
import psycopg2

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, CallbackContext

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


def create_database_buttons(database_list):
    buttons = []

    for database in database_list:
        button = InlineKeyboardButton(database, callback_data=f"select_db:{database}")
        buttons.append([button])

    return InlineKeyboardMarkup(buttons)


async def select_database_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    selected_database = query.data.split(":")[1]
    active_sessions_count = get_active_sessions_count(selected_database)

    message = f"Active sessions in {selected_database}: {active_sessions_count}"


    await query.message.reply_text(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def monitor(update: Update, context: CallbackContext):
    database_list = get_database_list()
    if database_list:
        message = "Select a database to view active sessions:"
        buttons = create_database_buttons(database_list)
        await update.message.reply_text(message, reply_markup=buttons)
    else:
        await update.message.reply_text("No databases found.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('API_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    monitor_handler = CommandHandler('monitor', monitor)
    application.add_handler(monitor_handler)

    select_database_button_handler = CallbackQueryHandler(select_database_button)
    application.add_handler(select_database_button_handler)


    application.run_polling()
