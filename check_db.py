import sqlite3

DB_NAME = "chatbot_database.db"  # Ensure this matches your actual database file

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Check table structure
c.execute("PRAGMA table_info(users);")
columns = [col[1] for col in c.fetchall()]

if "gender" in columns:
    print("✅ The 'gender' column exists in the users table.")
else:
    print("❌ The 'gender' column is missing. Adding it now...")
    c.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'Unknown'")
    conn.commit()
    print("✅ 'gender' column added successfully!")

conn.close()
