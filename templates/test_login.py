import sqlite3

identifier = "admin1"
password = "adminpass123"

conn = sqlite3.connect("data/usalama.db")
sql = conn.cursor()

sql.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?", 
            (identifier, identifier, password))
user = sql.fetchone()
conn.close()

if user:
    print("✅ Found:", user)
else:
    print("❌ No user found.")
