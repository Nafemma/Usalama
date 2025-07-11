import sqlite3
from werkzeug.security import generate_password_hash


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


# Generate hashed password
hashed_password = generate_password_hash('adminpass123')

# CHECK IF ADMIN1 ALREADY EXISTS
sql.execute("SELECT * FROM users WHERE username = 'admin1'")
existing_admin = sql.fetchone()

if not existing_admin:
    sql.execute('''
        INSERT INTO users (full_name, username, email, phone, password, role, due_date, language, linked_mother_username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Alinafe Mpofu',
        'admin1',
        'mpofuemmanuellah@gmail.com',
        '0885724876',
        hashed_password,
        'admin',
        None,
        'english',
        None
    ))
    print(" Default admin1 added.")
else:
    print("Admin1 already exists. Skipping insert.")


# ADMIN2
sql.execute("SELECT * FROM users WHERE username = 'admin2'")
existing_admin2 = sql.fetchone()

if not existing_admin2:
    sql.execute('''
        INSERT INTO users (full_name, username, email, phone, password, role, due_date, language, linked_mother_username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Alinafe Mpofu',
        'admin2',
        'mpofucynthias@gmail.com',
        '0882700581',
        hashed_password,
        'admin',
        None,
        'english',
        None
    ))
    print(" Default admin2 added.")
else:
    print("Admin2 already exists. Skipping insert.")



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
    username TEXT NOT NULL,
    mood TEXT NOT NULL,
    notes TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
)
    ''')
    print(" 'mood_logs' table created successfully.")
except Exception as e:
    print(" Error creating 'mood_logs' table:", e)



# LOGIN ATTEMPTS TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            username TEXT PRIMARY KEY,
            failed_attempts INTEGER DEFAULT 0,
            last_attempt TIMESTAMP
        )
    ''')
    print(" 'login_attempts' table created successfully.")
except Exception as e:
    print(" Error creating 'login_attempts' table:", e)

# PASSWORD RESET TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            email TEXT PRIMARY KEY,
            token TEXT,
            created_at TIMESTAMP
        )
    ''')
    print(" 'password_resets' table created successfully.")
except Exception as e:
    print(" Error creating 'password_resets' table:", e)
    
# PREGNANCY TRIMESTER TIPS TABLE
try:
    sql.execute('''
        CREATE TABLE IF NOT EXISTS trimester_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trimester TEXT NOT NULL,  
            tip_text TEXT NOT NULL,
            language TEXT DEFAULT 'english',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print(" 'trimester_tips' table created successfully.")
except Exception as e:
    print(" Error creating 'trimester_tips' table:", e)


# Finalize
conn.commit()
conn.close()
print("\n Database setup complete.")
