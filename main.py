from os import getenv
from dotenv import load_dotenv

from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from telegram_bot import (
    start, metrics, database,
    list_active_sessions, kill_session, checkpoint_and_restart,
    cpu, disk, ram,
    unknown, select_option, send_log
)


def main():
    # load .env variables
    load_dotenv()

    print('PostgreMonitorBot started')

    application = ApplicationBuilder().token(getenv('API_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    database_handler = CommandHandler('database', database)
    application.add_handler(database_handler)

    metrics_handler = CommandHandler('metrics', metrics)
    application.add_handler(metrics_handler)

    list_active_sessions_handler = CommandHandler('activesessions', list_active_sessions)
    application.add_handler(list_active_sessions_handler)

    kill_handler = CommandHandler('kill', kill_session)
    application.add_handler(kill_handler)

    restart_database_handler = CommandHandler('checkpointrestart', checkpoint_and_restart)
    application.add_handler(restart_database_handler)

    cpu_handler = CommandHandler('cpu', cpu)
    application.add_handler(cpu_handler)

    disk_handler = CommandHandler('disk', disk)
    application.add_handler(disk_handler)

    ram_handler = CommandHandler('ram', ram)
    application.add_handler(ram_handler)

    log_handler = CommandHandler('sendlog', send_log)
    application.add_handler(log_handler)

    unknown_handler = MessageHandler(filters.Command(False), unknown)
    application.add_handler(unknown_handler)

    select_option_handler = CallbackQueryHandler(select_option)
    application.add_handler(select_option_handler)

    print('Polling...')

    application.run_polling()


if __name__ == '__main__':
    main()
