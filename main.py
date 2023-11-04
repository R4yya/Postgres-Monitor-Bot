from os import getenv
from dotenv import load_dotenv

from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from telegram_bot import (
    start, stats, terminate_all_sessions,
    cpu, disk, unknown,
    select_option
)


# Global variables
selected_database = None
selected_metric = None


def main():
    # load .env variables
    load_dotenv()

    application = ApplicationBuilder().token(getenv('API_TOKEN')).build()

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


if __name__ == '__main__':
    main()
