
#!!! Run this ONCE to create all database tables !!!
import dotenv
import sys
import os

# Project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import init_database

def setup_database():
    dotenv.load_dotenv()

    try:
        connection_string = os.environ.get("DB_CONNECTION_STRING", "")
        if not connection_string:
            raise ValueError("DB_CONNECTION_STRING not set in .env")
    except Exception as e:
        print("Failed to read DB_CONNECTION_STRING from .env, make sure it exists and is correct.")
        print(f"Error: {e}")
        return
    
    print(f"Connecting to: {connection_string} ⏳")
    
    try:
        manager = init_database(connection_string)
        
        if manager is None:
            print("ERROR: init_database returned None!")
            return
        
        manager.create_tables()
        print("[✓] Database tables created successfully! You can now run the server!")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        return

if __name__ == "__main__":
    setup_database()