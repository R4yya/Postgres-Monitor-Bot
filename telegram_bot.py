from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

from database import (
    create_db_connection, execute_sql_query, get_database_list,
    get_active_sessions, terminate_all_sessions, get_sessions_with_lwlock,
    get_longest_transaction_duration
)
from utils import get_cpu_usage, get_disk_space_info

# Global variables
selected_database = None
selected_metric = None


def create_database_menu(database_list):
    database_menu = []
    for database in database_list:
        button = InlineKeyboardButton(
            database,
            callback_data=f'select_db:{database}'
        )
        database_menu.append([button])

    return InlineKeyboardMarkup(database_menu)


def create_metrics_menu():
    metrics_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton('Active Sessions', callback_data='active_sessions')],
        [InlineKeyboardButton('Sessions with LWLock', callback_data='sessions_with_lwlock')],
        [InlineKeyboardButton('Longest Transaction Duration', callback_data='longest_transaction_duration')]
    ])

    return metrics_menu


async def check_active_sessions(context: CallbackContext, max_active_sessions=100):
    if selected_database:
        active_sessions_count = get_active_sessions(selected_database)
        if active_sessions_count > max_active_sessions:
            await context.bot.send_message(context.job.chat_id, f'Too many active sessions in the database! - {active_sessions_count}')
    else:
        await context.bot.send_message(context.job.chat_id, f"Can't monitor active sessions: database not selected")


async def check_cpu_usage(context: CallbackContext, max_cpu_usage=90):
    cpu_percentage = get_cpu_usage()
    if cpu_percentage > max_cpu_usage:
        await context.bot.send_message(context.job.chat_id, f'High CPU usage! - {max_cpu_usage}%')


async def check_disk_space(context: CallbackContext, min_disk_space=1):
    free_space, total_space, percentage_space = get_disk_space_info()
    if free_space < min_disk_space:
        await context.bot.send_message(context.job.chat_id, f'Low disk space! - {free_space:.2f}Gb')


async def select_option(update: Update, context: CallbackContext):
    query = update.callback_query
    global selected_database, selected_metric

    if query.data.startswith('select_db:'):
        selected_database = query.data.split(':')[1]
        back_button = InlineKeyboardButton('Back', callback_data='back_db')
        await query.message.edit_text(f'Database selected! {selected_database}', reply_markup=InlineKeyboardMarkup([[back_button]]))
    elif query.data == 'back':
        if selected_metric:
            selected_metric = None
            metrics_menu = create_metrics_menu()
            await query.message.edit_text('Select a metric:', reply_markup=metrics_menu)
    elif query.data == 'back_db':
        if selected_database:
            selected_database = None
            database_list = get_database_list()
            database_menu = create_database_menu(database_list)
            await query.message.edit_text('Select database:', reply_markup=database_menu)
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
    else:
        await context.bot.send_message(context.job.chat_id, f'{selected_database}')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm your PostgreSQL database monitoring bot"
    )

    context.job_queue.run_repeating(
        check_active_sessions,
        interval=15,
        first=0,
        chat_id=update.message.chat_id
    )
    context.job_queue.run_repeating(
        check_cpu_usage,
        interval=15,
        first=0,
        chat_id=update.message.chat_id
    )
    context.job_queue.run_repeating(
        check_disk_space,
        interval=15,
        first=0,
        chat_id=update.message.chat_id
    )


async def unknown(update: Update, context: CallbackContext):
    if selected_database:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command."
        )
    else:
        await update.message.reply_text('Please select a database first.')


async def metrics(update: Update, context: CallbackContext):
    metrics_menu = create_metrics_menu()
    await update.message.reply_text('Select a metric:', reply_markup=metrics_menu)


async def database(update: Update, context: CallbackContext):
    database_list = get_database_list()
    if database_list:
        if database_list != 'An error occurred while retrieving database list.':
            database_menu = create_database_menu(database_list)
            await update.message.reply_text('Select a database:', reply_markup=database_menu)
        else:
            await update.message.reply_text(f'{database_list}')
    else:
        await update.message.reply_text('No databases found.')


async def kill(update: Update, context: CallbackContext):
    if selected_database:
        try:
            connection = create_db_connection()
            query = f"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = '{selected_database}';"
            execute_sql_query(connection, query)
            await update.message.reply_text(f'All sessions in {selected_database} have been terminated.')
        except Exception as e:

            await update.message.reply_text(f'An error occurred while terminating sessions.')
    else:
        await update.message.reply_text('Please select a database first.')


async def cpu(update: Update, context: CallbackContext):
    cpu_percentage = get_cpu_usage()
    await update.message.reply_text(f'CPU information:\nCPU usage: {cpu_percentage}%')


async def disk(update: Update, context: CallbackContext):
    free_space, total_space, percentage_space = get_disk_space_info()
    await update.message.reply_text(f'*Disk space:*\n\tFree: {free_space:.2f} GB\n\tTotal: {total_space:.2f} GB\n\tUsage: {percentage_space}%', parse_mode= 'Markdown')
