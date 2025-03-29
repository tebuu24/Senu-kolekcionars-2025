import sqlite3

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS senes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nosaukums TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS lokacija (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nosaukums TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS kolekcijas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lietotajs_id INTEGER NOT NULL,
            senes_id INTEGER NOT NULL,
            lokacija_id INTEGER NOT NULL,
            attels BLOB NOT NULL,
            datums DATE NOT NULL,
            skaits INTEGER NOT NULL,
            FOREIGN KEY (lietotajs_id) REFERENCES lietotaji(id) ON DELETE CASCADE,
            FOREIGN KEY (senes_id) REFERENCES senes(id) ON DELETE CASCADE,
            FOREIGN KEY (lokacija_id) REFERENCES lokacija(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pazinojumi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            saturs TEXT,
            kolekcijas_id INTEGER,
            laiks DATETIME NOT NULL,
            FOREIGN KEY (kolekcijas_id) REFERENCES kolekcijas(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

initialize_database()
