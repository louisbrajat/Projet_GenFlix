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
    img_url TEXT,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS Like (
    user_id INTEGER,
    serie_id INTEGER,
    Note REAL,
    PRIMARY KEY (user_id, serie_id),
    FOREIGN KEY (user_id) REFERENCES User(ID),
    FOREIGN KEY (serie_id) REFERENCES Serie(IDTvMaze)
);
"""
cursor.executescript(schema)
conn.commit()