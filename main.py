from scraping.ftse_scraper import FTSEScraper
from db.database import DatabaseManager
from scraping.target_scraper import RecommendationScraper
if __name__ == "__main__":
    ftse_scraper = FTSEScraper()
    ftse_list = ftse_scraper.fetch()
    print("FTSE: ", ftse_list)
    recomm_scraper = RecommendationScraper(ftse_list)
    recomm_list = recomm_scraper.fetch()
    print("Recommendations: ", recomm_list)
    db = DatabaseManager()
    db.save_ftse_list(ftse_list)
    db.save_recommendations(recomm_list)
    db.close()