# [Telegram Database Monitor Bot.](https://t.me/postgres_monitor_bot)
## _Telegram bot for monitoring PostgreSQL database_

- The Telegram Database Monitor Bot is a tool for real-time monitoring of your PostgreSQL database, designed to help you stay updated on the database's status and receive notifications on various events.

## Tech
- Python
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- PostgreSQL

## Installation
Requires Python 3.6+ to run.

To run the Telegram Database Monitor Bot:

1. Clone the repository:

```sh
git clone https://github.com/R4yya/Postgres-Monitor-Bot.git
```
Install the required Python packages:
```sh
pip install python-telegram-bot psycopg2 python-dotenv
```
Set up your PostgreSQL. Also add your bot key and dase info for connection in .env file

Run the bot:
```sh
python -m bot.py
```
Usage
Start the bot on Telegram and follow the instructions to configure the database monitoring settings.
## BTW
You can check the Telegram Database Monitor Bot on [Monitor Bot](https://t.me/postgres_monitor_bot)
