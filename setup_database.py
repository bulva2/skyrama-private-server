"""
!!! Run this ONCE to create all database tables !!!
"""

import sys
import os

# Project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import init_database
from src.configHandler import get_config

def setup_database():
    config = get_config()

    try:
        connection_string = config.get(
            "Database", 
            "connection_string"
        )
    except Exception as e:
        print("Failed to read database connection string from config. Make sure it is there.")
        print(f"Error: {e}")
        return
    
    print(f"Connecting to: {connection_string}")
    
    try:
        manager = init_database(connection_string)
        
        if manager is None:
            print("ERROR: init_database returned None!")
            return
        
        manager.create_tables()
        print("[✓] Database tables created successfully! You can now run the server!")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    setup_database()