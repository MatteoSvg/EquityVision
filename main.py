from scraping.ftse_scraper import FTSEScraper
from db.database import DatabaseManager
from scraping.target_scraper import RecommendationScraper
from datetime import date
from utils import csv_writer
from gui import EquityVisionGUI

if __name__ == "__main__":
    # Inizializza il database
    db = DatabaseManager()
    
    # Scraping FTSE
    print("Recupero dati FTSE MIB...")
    ftse_scraper = FTSEScraper()
    ftse_list = ftse_scraper.fetch()
    db.save_ftse_list(ftse_list)
    csv_writer.export_stocks(ftse_list)
    
    # Scraping raccomandazioni
    print("Recupero raccomandazioni...")
    recomm_scraper = RecommendationScraper(ftse_list)
    recomm_list = recomm_scraper.fetch(db)
    db.save_recommendations(recomm_list)
    csv_writer.export_recommendations(db)
    
    print("Apertura interfaccia grafica...")
    # Avvia l'interfaccia grafica (passa il db come parametro)
    app = EquityVisionGUI(db)
    app.run()
    
    # Chiudi il database quando l'interfaccia viene chiusa
    db.close()
    print("Applicazione terminata.")