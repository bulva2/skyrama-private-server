
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()
conn_str = os.environ.get("DB_CONNECTION_STRING", None)
if not conn_str:
    print("No DB_CONNECTION_STRING found in .env file.")


def test_connection():
    if not conn_str:
        print("No connection string available, aborting.")
        return

    try:
        with psycopg.connect(conn_str) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()

                print("Connected! You did everything right, give yourself a pat on the back!")
                print(f"Database version: {db_version[0]}")
    except psycopg.OperationalError as e:
        print("Connection failed!")
        print(f"Error: {e}")
    except Exception as exc:
        print("Error while connecting!")
        print(f"Error: {exc}")


if __name__ == "__main__":
    test_connection()