import csv
import os

def export_recommendations(db):
    '''
    Funzione: export_recommendations
    Esporta le raccomandazioni trovate nel database in un file CSV
    Parametri formali:
    object db -> Oggetto database da cui estrarre le raccomandazioni
    Valore di ritorno:
    None -> Nessun valore di ritorno.
    '''
    # Crea la cartella data se non esiste
    os.makedirs("data", exist_ok=True)
    
    # Rimuove il file se esiste già
    file_path = "data/recommendations.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    
    recommendations = db.find_recommendations()
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f) #mi salvo l'oggetto writer per scrivere sul file
        writer.writerow(["name", "bank", "target_price", "date", "market_price"])
        # Scrive ogni tupla come una riga nel file
        writer.writerows(recommendations)

def export_stocks(stocks_list):
    '''
    Funzione: export_stocks
    Esporta una lista di azioni (titoli) in un file CSV
    Parametri formali:
    list stocks_list -> Lista di azioni da esportare. Ogni elemento è una tupla/lista contenente i dati del titolo.
    Valore di ritorno:
    None -> Nessun valore di ritorno.
    '''
    # Crea la cartella data se non esiste
    os.makedirs("data", exist_ok=True)
    
    # Rimuove il file se esiste già
    file_path = "data/ftse.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f) 
        writer.writerow(["name", "market_price"])
        for stock in stocks_list:
            writer.writerow([stock[1], stock[2]])