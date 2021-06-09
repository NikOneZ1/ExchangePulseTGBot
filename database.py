import sqlite3


class DB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        with self.conn:
            self.cursor.execute(""" CREATE TABLE IF NOT EXISTS rates (
                                        ID integer PRIMARY KEY,
                                        output text NOT NULL,
                                        timestamp text
                                        ); """)

    def add_rates(self, data):
        with self.conn:
            self.cursor.execute("INSERT INTO rates(output, timestamp) VALUES(?, ?)", data)
        self.conn.commit()

    def get_latest_rates(self):
        with self.conn:
            self.cursor.execute("SELECT * FROM rates ORDER BY ID DESC LIMIT 1")
        return(self.cursor.fetchall())
