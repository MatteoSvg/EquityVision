from scraping.ftse_scraper import FTSEScraper
from db.database import DatabaseManager
from scraping.target_scraper import RecommendationScraper
from datetime import date
from utils import csv_writer
from gui import EquityVisionGUI

if __name__ == "__main__":

    db = DatabaseManager() 
    print("Recupero dati FTSE MIB...")
    ftse_scraper = FTSEScraper()
    ftse_list = ftse_scraper.fetch()
    db.save_ftse_list(ftse_list)
    csv_writer.export_stocks(ftse_list)

    print("Recupero raccomandazioni...")
    recomm_scraper = RecommendationScraper(ftse_list)
    recomm_list = recomm_scraper.fetch(db)
    db.save_recommendations(recomm_list)
    csv_writer.export_recommendations(db)

    print("Apertura interfaccia grafica...")
    app = EquityVisionGUI(db)
    app.run()
 
    db.close()
    print("Applicazione terminata.")