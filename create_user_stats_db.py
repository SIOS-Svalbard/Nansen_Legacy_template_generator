import sqlite3
import os
import sys

def create_db():
    db_filename = 'visits.db'

    # Check if the database file already exists
    if os.path.exists(db_filename):
        print(f"Database '{db_filename}' already exists. Exiting.")
        sys.exit(0)  # Exit the script if the database exists

    print(f"Creating new database '{db_filename}'.")

    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

    # Create 'visits' table
    c.execute('''CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ip TEXT,
                    country TEXT
                )'''
            )

    # Create 'templates' table
    c.execute('''CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ip TEXT,
                    country TEXT,
                    config TEXT,
                    subconfig TEXT,
                    sheets TEXT
                )'''
            )

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

# Entry point for execution
if __name__ == '__main__':
    create_db()