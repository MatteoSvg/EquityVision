# import csv
# import os

# def export_recommendations(db):
#     # Crea la cartella data se non esiste
#     os.makedirs("data", exist_ok=True)
    
#     recommendations = db.find_recommendations()
#     with open("data/recommendations.csv", mode="w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["name", "bank", "target_price", "date"])
#         # Scrive ogni tupla come una riga nel file
#         writer.writerows(recommendations)

# def export_stocks(stocks_list):
#     # Crea la cartella data se non esiste
#     os.makedirs("data", exist_ok=True)
    
#     with open("data/ftse.csv", mode="w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["name", "market_price"])
#         for stock in stocks_list:
#             writer.writerow([stock[1], stock[2]])

import csv
import os

def export_recommendations(db):
    # Crea la cartella data se non esiste
    os.makedirs("data", exist_ok=True)
    
    # Rimuove il file se esiste già
    file_path = "data/recommendations.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    
    recommendations = db.find_recommendations()
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "bank", "target_price", "date"])
        # Scrive ogni tupla come una riga nel file
        writer.writerows(recommendations)

def export_stocks(stocks_list):
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