import requests
from bs4 import BeautifulSoup

class FTSEScraper:
    """Classe per estrarre i titoli FTSE MIB e il loro ultimo prezzo da borses.it"""
    
    def __init__(self):
        self.url = "https://www.borse.it/quotazioni/paniere/borsa-italiana/ITA-40"
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        self.data = []

    def fetch(self):
        response = requests.get(self.url, headers=self.headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find("tbody").find_all("tr")

        self.data = []
        for row in rows:
            cells = row.find_all("td")
            nome = cells[0].text.strip().upper()
            prezzo = cells[1].text
            self.data.append((nome, prezzo))  # nome in maiuscolo per uniformità
        return self.data