import sqlite3

print(" Creating Usalama database...")

# Connect to the database
try:
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    print(" Connected to database.")
except Exception as e:
    print(" Failed to connect:", e)

# USERS TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            username TEXT UNIQUE,
            email TEXT,
            phone TEXT,
            password TEXT,
            role TEXT,
            due_date TEXT,
            language TEXT
        )
    ''')
    print(" 'users' table created successfully.")
except Exception as e:
    print(" Error creating 'users' table:", e)

# TEXT TIPS TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS text_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            keyword_or_week TEXT,
            language TEXT,
            tip_text TEXT
        )
    ''')
    print(" 'text_tips' table created successfully.")
except Exception as e:
    print(" Error creating 'text_tips' table:", e)

# AUDIO TIPS TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS audio_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            keyword_or_week TEXT,
            language TEXT,
            filename TEXT
        )
    ''')
    print(" 'audio_tips' table created successfully.")
except Exception as e:
    print(" Error creating 'audio_tips' table:", e)

# MOOD LOGS TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            username TEXT,
            mood TEXT,
            notes TEXT
        )
    ''')
    print(" 'mood_logs' table created successfully.")
except Exception as e:
    print(" Error creating 'mood_logs' table:", e)

# Finalize
conn.commit()
conn.close()
print("\n Database setup complete.")
