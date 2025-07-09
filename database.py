import sqlite3

print(" Creating Usalama database...")

# Connect to the database
try:
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    print(" Connected to database.")
except Exception as e:
    print(" Failed to connect:", e)



# USERS TABLE (Mothers, Partners, Admins)
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            phone TEXT,
            password TEXT NOT NULL,
            role TEXT NOT NULL, -- mother, partner, admin
            linked_mother_username TEXT, 
            due_date TEXT, -- for mothers only
            language TEXT
        )
    ''')
    print(" 'users' table created successfully.")
except Exception as e:
    print(" Error creating 'users' table:", e)


#CHECK IF ADMIN ALREADY EXISTS
sql.execute("SELECT * FROM users WHERE username = 'admin1'")
existing_admin = sql.fetchone()

# ADMIN1: IF NO ADMIN EXISTS, INSERT DEFAULT ADMIN
if not existing_admin:
    sql.execute('''
        INSERT INTO users (full_name, username, email, phone, password, role, due_date, language, linked_mother_username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Alinafe Mpofu',
        'admin1',
        'mpofuemmanuellah@gmail.com',
        '0885724876',
        'adminpass123',
        'admin',
        None,
        'english',
        None
    ))
    print(" Default admin added.")
else:
    print("Admin already exists. Skipping insert.")



# TEXT TIPS TABLE
try:
    sql.execute('''
    CREATE TABLE IF NOT EXISTS text_tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tip_type TEXT NOT NULL,        -- 'weekly' or 'ondemand'
        week_number INTEGER,           -- NULL if ondemand
        keyword TEXT,                  -- NULL if weekly
        language TEXT NOT NULL,
        content TEXT NOT NULL
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
        tip_type TEXT NOT NULL,
        week_number INTEGER,
        keyword TEXT,
        language TEXT NOT NULL,
        file_path TEXT NOT NULL
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
