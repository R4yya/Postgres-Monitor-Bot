from dotenv import load_dotenv
import logging
import psycopg2
import psutil
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    CallbackQueryHandler, CallbackContext, MessageHandler,
    filters, Job)

# Logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Global variables
selected_database = None
selected_metric = None


def create_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv('HOST'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD')
        )
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')


def execute_sql_query(connection, query):
    with connection, connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_database_list():
    try:
        connection = create_db_connection()
        query = 'SELECT datname FROM pg_database;'
        database_list = execute_sql_query(connection, query)

        if database_list:
            return [row[0] for row in database_list]
        else:
            return []
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving database list.'


def get_active_sessions(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '{database_name}';"
        result = execute_sql_query(connection, query)

        if result:
            return result[0][0]
        else:
            return 0
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving session information.'


def terminate_all_sessions(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = '{database_name}';"
        execute_sql_query(connection, query)
        return f'All sessions in {database_name} have been terminated.'
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return f'An error occurred while terminating sessions.'


def get_sessions_with_lwlock(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '{database_name}' AND wait_event LIKE 'LWLock%';"
        result = execute_sql_query(connection, query)

        if result:
            return result[0][0]
        else:
            return 0
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving session information.'


def get_longest_transaction_duration(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT max(now() - pg_stat_activity.query_start) AS longest_transaction_duration FROM pg_stat_activity WHERE datname = '{database_name}';"
        result = execute_sql_query(connection, query)

        if result:
            return result[0][0]
        else:
            return 'No active transactions found.'
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving transaction information.'


def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    return cpu_percent


def get_disk_free_space():
    disk = psutil.disk_usage('/')
    free_space = disk.free / (1024 ** 3)
    return free_space


def create_database_buttons(database_list):
    buttons = []

    for database in database_list:
        button = InlineKeyboardButton(database, callback_data=f'select_db:{database}')
        buttons.append([button])

    return InlineKeyboardMarkup(buttons)


def create_metrics_menu():
    metrics_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton('Active Sessions', callback_data='active_sessions')],
        [InlineKeyboardButton('Sessions with LWLock', callback_data='sessions_with_lwlock')],
        [InlineKeyboardButton('Longest Transaction Duration', callback_data='longest_transaction_duration')],
        [InlineKeyboardButton('Back', callback_data='back')]
    ])

    return metrics_menu


async def check_active_sessions(context: CallbackContext, max_active_sessions=100):
    if selected_database:
        active_sessions_count = int(get_active_sessions(selected_database))
        if active_sessions_count > max_active_sessions:
            await context.bot.send_message(context.job.chat_id, f'Too many active sessions in the database! - {active_sessions_count}')


async def check_cpu_usage(context: CallbackContext, max_cpu_usage=90):
    cpu_percent = get_cpu_usage()
    if cpu_percent > max_cpu_usage:
        await context.bot.send_message(context.job.chat_id, f'High CPU usage! - {max_cpu_usage}%')


async def check_disk_space(context: CallbackContext, min_disk_space=1):
    disk_space = get_disk_free_space()
    if disk_space < min_disk_space:
        await context.bot.send_message(context.job.chat_id, f'Low disk space! - {disk_space:.2f}Gb')


async def select_option(update: Update, context: CallbackContext):
    query = update.callback_query
    global selected_database, selected_metric

    if query.data.startswith('select_db:'):
        selected_database = query.data.split(':')[1]
        metrics_menu = create_metrics_menu()
        await query.message.edit_text('Select a metric:', reply_markup=metrics_menu)
    elif query.data == 'back':
        if selected_metric:
            selected_metric = None
            metrics_menu = create_metrics_menu()
            await query.message.edit_text('Select a metric:', reply_markup=metrics_menu)
        else:
            selected_database = None
            database_list = get_database_list()
            buttons = create_database_buttons(database_list)
            await query.message.edit_text('Select a database:', reply_markup=buttons)
    elif query.data == 'active_sessions':
        selected_metric = query.data
        if selected_database:
            active_sessions_count = get_active_sessions(selected_database)
            message = f'Active sessions in {selected_database}: {active_sessions_count}'
            back_button = InlineKeyboardButton('Back', callback_data='back')
            await query.message.edit_text(message, reply_markup=InlineKeyboardMarkup([[back_button]]))
        else:
            await query.message.edit_text('Please select a database first.')
    elif query.data == 'sessions_with_lwlock':
        selected_metric = query.data
        if selected_database:
            sessions_with_lwlock_count = get_sessions_with_lwlock(selected_database)
            message = f'Sessions with LWLock in {selected_database}: {sessions_with_lwlock_count}'
            back_button = InlineKeyboardButton('Back', callback_data='back')
            await query.message.edit_text(message, reply_markup=InlineKeyboardMarkup([[back_button]]))
        else:
            await query.message.edit_text('Please select a database first.')
    elif query.data == 'longest_transaction_duration':
        selected_metric = query.data
        if selected_database:
            longest_transaction_duration = get_longest_transaction_duration(selected_database)
            message = f'Longest transaction duration in {selected_database}: {longest_transaction_duration}'
            back_button = InlineKeyboardButton('Back', callback_data='back')
            await query.message.edit_text(message, reply_markup=InlineKeyboardMarkup([[back_button]]))
        else:
            await query.message.edit_text('Please select a database first.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm your PostgreSQL database monitoring bot"
    )

    context.job_queue.run_repeating(check_active_sessions, interval=15, first=0, chat_id=update.message.chat_id)
    context.job_queue.run_repeating(check_cpu_usage, interval=15, first=0, chat_id=update.message.chat_id)
    context.job_queue.run_repeating(check_disk_space, interval=15, first=0, chat_id=update.message.chat_id)


async def unknown(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )


async def stats(update: Update, context: CallbackContext):
    database_list = get_database_list()
    if database_list:
        message = 'Select a database:'
        buttons = create_database_buttons(database_list)
        await update.message.reply_text(message, reply_markup=buttons)
    else:
        await update.message.reply_text('No databases found.')


async def terminate_all_sessions(update: Update, context: CallbackContext):
    if selected_database:
        try:
            connection = create_db_connection()
            query = f"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = '{selected_database}';"
            execute_sql_query(connection, query)
            await update.message.reply_text(f'All sessions in {selected_database} have been terminated.')
        except Exception as e:
            logging.error(f'An error occurred: {str(e)}')
            await update.message.reply_text(f'An error occurred while terminating sessions.')
    else:
        await update.message.reply_text('Please select a database first.')


async def cpu(update: Update, context: CallbackContext):
    cpu_usage = get_cpu_usage()
    await update.message.reply_text(f'CPU usage: {cpu_usage}%')


async def disk(update: Update, context: CallbackContext):
    disk_space = get_disk_free_space()[0]
    await update.message.reply_text(f'Free disk space: {disk_space:.2f} GB')


if __name__ == '__main__':
    # load .env variables
    load_dotenv()

    application = ApplicationBuilder().token(os.getenv('API_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    monitor_handler = CommandHandler('stats', stats)
    application.add_handler(monitor_handler)

    terminate_sessions_handler = CommandHandler('kill', terminate_all_sessions)
    application.add_handler(terminate_sessions_handler)

    cpu_handler = CommandHandler('cpu', cpu)
    application.add_handler(cpu_handler)

    disk_handler = CommandHandler('disk', disk)
    application.add_handler(disk_handler)

    unknown_handler = MessageHandler(filters.Command(False), unknown)
    application.add_handler(unknown_handler)

    select_option_handler = CallbackQueryHandler(select_option)
    application.add_handler(select_option_handler)

    application.run_polling()
