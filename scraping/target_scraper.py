import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from db.database import DatabaseManager
class RecommendationScraper:
    """Classe per estrarre le raccomandazioni dal sito soldionline.it"""

    def __init__(self, ftse_list):
        self.ftse_list = ftse_list
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        self.mesi = {
            1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
            5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
            9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre",
        }

    def fetch(self, db, start_date=date(2025, 9, 22), end_date=None):
        if end_date is None:
            end_date = date.today()

        recommendations = []
        next_date = start_date

        while next_date < end_date:
            url = (f"https://www.soldionline.it/notizie/azioni-italia/"
                   f"le-raccomandazioni-del-{next_date.day}-"
                   f"{self.mesi[next_date.month]}-{next_date.year}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 404:
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.find("tbody").find_all("tr")

                for row in rows:
                    cells = row.find_all("td")
                    society = cells[0].text.strip().upper()
                    bank = cells[1].text.strip()
                    target_price = cells[3].text.strip().replace("▲", "").replace("▼", "")

                    # filtro solo società FTSE
                    for i in range(len(self.ftse_list)):
                        if society == self.ftse_list[i][0]:
                            id_company = db.find_company_id(society)
                            recommendations.append((id_company, bank, target_price, next_date))
            next_date += timedelta(days=1)

        return recommendations
