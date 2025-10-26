import os
import configparser
import psycopg2
from psycopg2 import OperationalError

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(ROOT, "config.cfg")

config = configparser.ConfigParser()
read_ok = config.read(CONFIG_PATH)

conn_str = None
if config.has_section("Database") and config.has_option("Database", "connection_string"):
    conn_str = config.get("Database", "connection_string")
else:
    print(f"No connection_string found in {CONFIG_PATH} under [Database]")


def test_connection():
    if not conn_str:
        print("No connection string available, aborting.")
        return

    try:
        connection = psycopg2.connect(conn_str)
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()

        print("Connected! You did everything right, give yourself a pat on the back!")
        print(f"Database version: {db_version[0]}")

        cursor.close()
        connection.close()

    except OperationalError as e:
        print("Connection failed!")
        print(f"Error: {e}")
    except Exception as exc:
        print("Error while connecting!")
        print(f"Error: {exc}")


if __name__ == "__main__":
    test_connection()