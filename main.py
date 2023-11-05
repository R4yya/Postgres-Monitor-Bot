from os import getenv
from dotenv import load_dotenv

from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from telegram_bot import (
    start, metrics, database,
    kill, cpu, disk,
    ram, unknown, select_option,
    send_log
)


def main():
    # load .env variables
    load_dotenv()

    application = ApplicationBuilder().token(getenv('API_TOKEN')).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    database_handler = CommandHandler('database', database)
    application.add_handler(database_handler)

    metrics_handler = CommandHandler('metrics', metrics)
    application.add_handler(metrics_handler)

    kill_handler = CommandHandler('kill', kill)
    application.add_handler(kill_handler)

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

    application.run_polling()


if __name__ == '__main__':
    main()
