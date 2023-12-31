from psycopg2 import connect
from logging import (
    INFO, error,
    FileHandler, Formatter, getLogger
)
from os import getenv


# Logger
file_handler = FileHandler('PostgreMonitorBot.log')
file_handler.setLevel(INFO)
log_formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_formatter)
getLogger('').addHandler(file_handler)


def create_db_connection():
    try:
        return connect(
            host=getenv('HOST'),
            database=getenv('DATABASE_NAME'),
            user=getenv('USER'),
            password=getenv('PASSWORD')
        )
    except Exception as e:
        error(f'An error occurred: {str(e)}')


def execute_sql_query(connection, query):
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            error(f'An error occurred: {str(e)}')


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
        error(f'An error occurred: {str(e)}')

        return 'An error occurred while retrieving database list.'


def get_active_sessions(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT pid, usename, application_name, state FROM pg_stat_activity WHERE datname = '{database_name}';"
        result = execute_sql_query(connection, query)
        return result
    except Exception as e:
        error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving session information.'


def kill_specific_session(pid):
    try:
        connection = create_db_connection()
        query = f'SELECT pg_terminate_backend ({pid});'
        execute_sql_query(connection, query)
    except Exception as e:
        error(f'An error occurred: {str(e)}')


def execute_checkpoint_restart(database_name):
    try:
        connection = create_db_connection()

        checkpoint_query = 'CHECKPOINT;'
        execute_sql_query(connection, checkpoint_query)

        restart_query = f"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = '{database_name}';"
        execute_sql_query(connection, restart_query)
    except Exception as e:
        error(f'An error occurred: {str(e)}')


def get_sessions_with_lwlock(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '{database_name}' AND wait_event LIKE 'LWLock';"
        result = execute_sql_query(connection, query)

        if result:
            return result[0][0]
        else:
            return 0
    except Exception as e:
        error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving session information.'


def get_longest_transaction_duration(database_name):
    try:
        connection = create_db_connection()
        query = f"SELECT max(now() - pg_stat_activity.query_start) AS longest_transaction_duration FROM pg_stat_activity WHERE datname = '{database_name}';"
        result = execute_sql_query(connection, query)

        if result:
            return result[0][0]
        else:
            return '\nNo active transactions found.'
    except Exception as e:
        error(f'An error occurred: {str(e)}')

        return f'An error occurred while retrieving transaction information.'
