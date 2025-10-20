import sqlite3
import os
from datetime import datetime
class DatabaseManager:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), "equityvision")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database non trovato: {db_path}")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(" DROP TABLE IF EXISTS companies")
        self.cursor.execute("""
            CREATE TABLE companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isin TEXT,
                name TEXT NOT NULL,
                market_price REAL NOT NULL
            )
        """)
        # self.cursor.execute("DROP TABLE IF EXISTS recommendations")
        # self.cursor.execute("""
        #     CREATE TABLE recommendations (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         company_id TEXT NOT NULL,
        #         bank TEXT NOT NULL,
        #         target_price REAL,
        #         date DATE NOT NULL,
        #         CONSTRAINT FK_recommendations_companies FOREIGN KEY (company_id) REFERENCES companies(id)
        #     )
        # """)
        self.conn.commit()
        
    
    def save_ftse_list(self, ftse_list):
        for isin, company, price in ftse_list:
            try:
                self.cursor.execute(
                "INSERT INTO companies (isin, name, market_price) VALUES (?, ?, ?)",
                (isin, company, price)
            )
            except sqlite3.Error as e:
                print("Errore durante l'inserimento: ", e)
        self.conn.commit()

    def find_company_id(self, isin):
        """Restituisce il codice ISIN se esiste nella tabella companies, altrimenti None."""
        result = self.cursor.execute(
            "SELECT id FROM companies WHERE isin = ?", (isin,)
        ).fetchone()
        return result[0] if result else None

    
    def find_last_date(self):
        self.cursor.execute("SELECT MAX(date) FROM recommendations")
        result = self.cursor.fetchone()
        print(result)
        if result and result[0]:
            return datetime.strptime(result[0], "%Y-%m-%d").date()
        return None

        
       

    def save_recommendations(self, recomm_list):
        for id_company, bank, target_price, next_date in recomm_list:
            try:
                self.cursor.execute(
                "INSERT INTO recommendations (company_id, bank, target_price, date) VALUES (?, ?, ?, ?)",
                (id_company, bank, target_price, next_date)
            )
            except sqlite3.Error as e:
                print("Errore durante l'inserimento: ", e)
        self.conn.commit()

    def find_recommendations(self):
        return self.cursor.execute("SELECT c.name, r.bank, r.target_price, r.date FROM recommendations r JOIN companies c ON r.company_id = c.id").fetchall()
        
    def close(self):
        self.conn.close()



    
