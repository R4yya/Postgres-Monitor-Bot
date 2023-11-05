from psycopg2 import connect
from os import getenv
from dotenv import load_dotenv

load_dotenv()

host = getenv('HOST')
database_name = getenv('DATABASE_NAME')
user = getenv('USER')
password = getenv('PASSWORD')

try:
    connection = connect(
        host=host,
        database=database_name,
        user=user,
        password=password
    )

    cursor = connection.cursor()

    cursor.execute("SET application_name = 'test_invalid_session'")
    cursor.execute("SELECT pg_sleep(36000)")

    connection.commit()

    cursor.close()
    connection.close()

    print('Active session created succsessfully. Now you can use bot /kill command.')
except Exception as e:
    print(f'Error: {str(e)}')
