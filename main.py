from scraping.ftse_scraper import FTSEScraper
from db.database import DatabaseManager
from scraping.target_scraper import RecommendationScraper
from datetime import date
from utils import csv_writer
if __name__ == "__main__":
    db = DatabaseManager()
    ftse_scraper = FTSEScraper()
    ftse_list = ftse_scraper.fetch()
    print(ftse_list)
    db.save_ftse_list(ftse_list)
    # csv_writer.export_stocks(ftse_list)
    recomm_scraper = RecommendationScraper(ftse_list)
    recomm_list = recomm_scraper.fetch(db, date(2025,10,1), date(2025,10,15))
    print(recomm_list)
    db.save_recommendations(recomm_list)
    # csv_writer.export_recommendations(db)
    db.close()