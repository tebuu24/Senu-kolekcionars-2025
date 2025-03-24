import sqlite3

# Funkcija, lai izveidotu vai pārbaudītu datubāzi
def initialize_database():
    conn = sqlite3.connect("lietotaji.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lietotaji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Izsauc funkciju, lai nodrošinātu, ka datubāze pastāv
initialize_database()
