import sqlite3

conn = sqlite3.connect("instance/Genflix.db")
cursor = conn.cursor()

schema = """
CREATE TABLE IF NOT EXISTS User (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Email TEXT UNIQUE NOT NULL,
    Pseudo TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Serie (
    IDTvMaze INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    Note INTEGER,
    img TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES User(ID)
);
"""
cursor.executescript(schema)
conn.commit()