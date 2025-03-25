import sqlite3

# Database file name
DB_NAME = "emails.db"

def create_email_table():
    """Creates the emails table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT UNIQUE,
        sender TEXT,
        recipient TEXT,
        subject TEXT,
        body TEXT,
        timestamp TEXT,
        label TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Email table created successfully!")

# Run the function to create the table
if __name__ == "__main__":
    create_email_table()
