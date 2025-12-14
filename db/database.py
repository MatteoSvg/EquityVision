import sqlite3
import os
from datetime import datetime, date
class DatabaseManager:
    def __init__(self):
        '''
        Metodo: __init__
        Inizializza il gestore del database SQLite
        Parametri formali:
        Nessuno
        Valore di ritorno:
        Nessuno
        '''
        db_path = os.path.join(os.path.dirname(__file__), "equityvision") #costruisco il percorso per il file del database
        #se non esiste lancio eccezione
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database non trovato: {db_path}")
        self.conn = sqlite3.connect(db_path) #mi connetto al database e salvo la connessione in un oggettto conn
        self.cursor = self.conn.cursor() #creo il cursore che serve per eseguire query, leggere i risultati ecc..
        self.create_tables()

    def create_tables(self):
        '''
        Metodo: create_tables
        Crea le tabelle nel database eliminando e ricreando la tabella companies
        Parametri formali:
        Nessuno
        Valore di ritorno:
        Nessuno
        '''
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
        self.conn.commit() #serve per salvare in modo permanente le modifiche fatte al database durante la connessione.
        
    def save_ftse_list(self, ftse_list):
        '''
        Metodo: save_ftse_list
        Salva la lista dei titoli FTSE nel database
        Parametri formali:
        list ftse_list -> lista di tuple contenenti (isin, company, price)
        Valore di ritorno:
        Nessuno
        '''
        for isin, company, price in ftse_list:
            try:
                self.cursor.execute(
                "INSERT INTO companies (isin, name, market_price) VALUES (?, ?, ?)",
                (isin, company, price)
            )
            except sqlite3.Error as e:
                print("Errore durante l'inserimento: ", e)
        self.conn.commit()

    def find_company_id(self, isin) -> int:
        '''
        Funzione: find_company_id
        Cerca l'ID di una compagnia tramite il suo codice ISIN
        Parametri formali:
        str isin -> codice ISIN della compagnia da cercare
        Valore di ritorno:
        int -> ID della compagnia se trovata, altrimenti None
        '''
        result = self.cursor.execute(
            "SELECT id FROM companies WHERE isin = ?", (isin,)
        ).fetchone()
        return result[0] if result else None

    
    def find_last_date(self) -> date:
        '''
        Funzione: find_last_date
        Trova l'ultima data presente nella tabella recommendations
        Parametri formali:
        Nessuno
        Valore di ritorno:
        date -> ultima data presente nel database, None se non ci sono dati
        '''
        self.cursor.execute("SELECT MAX(date) FROM recommendations")
        result = self.cursor.fetchone()
        if result and result[0]:
            return datetime.strptime(result[0], "%Y-%m-%d").date()
        return None

    def save_recommendations(self, recomm_list):
        '''
        Metodo: save_recommendations
        Salva le raccomandazioni nel database
        Parametri formali:
        list recomm_list -> lista di tuple contenenti (id_company, bank, target_price, next_date)
        Valore di ritorno:
        Nessuno
        '''
        for id_company, bank, target_price, next_date in recomm_list:
            try:
                self.cursor.execute(
                "INSERT INTO recommendations (company_id, bank, target_price, date) VALUES (?, ?, ?, ?)",
                (id_company, bank, target_price, next_date)
            )
            except sqlite3.Error as e:
                print("Errore durante l'inserimento: ", e)
        self.conn.commit()

    def find_recommendations(self) -> list:
        '''
        Funzione: find_recommendations
        Recupera tutte le raccomandazioni con i dati delle compagnie associate
        Parametri formali:
        Nessuno
        Valore di ritorno:
        list -> lista di tuple contenenti (name, bank, target_price, date, market_price)
        '''
        return self.cursor.execute("SELECT c.name, r.bank, r.target_price, r.date, c.market_price FROM recommendations r JOIN companies c ON r.company_id = c.id").fetchall()
        
    def close(self):
        '''
        Metodo: close
        Chiude la connessione al database
        Parametri formali:
        Nessuno
        Valore di ritorno:
        Nessuno
        '''
        self.conn.close()



    
