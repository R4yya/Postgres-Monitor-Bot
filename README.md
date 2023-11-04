# [Telegram Database Monitor Bot.](https://t.me/postgres_monitor_bot)
## _Telegram bot for monitoring PostgreSQL database_

The Telegram Database Monitor Bot is a tool for real-time monitoring of your PostgreSQL database, designed to help you stay updated on the database's status and receive notifications on various events.
With this bot, you can select specific databases and access statistics on:

- Active sessions
- Sessions with LWLock
- Longest transaction duration

This allows you to have detailed insights into the performance and activity of your PostgreSQL databases.

## Tech
- [Python](https://www.python.org/)
- [Python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [PostgreSQL](https://www.postgresql.org/)

## Installation
Requires Python 3.6+ to run.

To run the Telegram Database Monitor Bot:

Clone the repository:
```sh
git clone https://github.com/R4yya/Postgres-Monitor-Bot.git
```
Install the required Python packages:
```sh
pip install -r requirements.txt
```
Set up your PostgreSQL database and dase info for connection in .env file

Run the bot:
```sh
python -m main.py
```
Usage
Start the bot on Telegram and follow the instructions to configure the database monitoring settings.
## Links
You can check the Telegram Database Monitor Bot on [Monitor Bot](https://t.me/postgres_monitor_bot)
