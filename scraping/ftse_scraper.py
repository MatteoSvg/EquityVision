import requests
from bs4 import BeautifulSoup
import re

class FTSEScraper:
    """Classe per estrarre i titoli FTSE MIB, il loro ultimo prezzo e il codice ISIN da borse.it"""

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
            if not cells:
                continue

            # Nome e ISIN
            link = cells[0].find("a")
            if link:
                nome = link.text.strip().upper()
                href = link.get("href", "")
                # Regex più generale: due lettere seguite da 10 caratteri alfanumerici
                isin_match = re.search(r"([A-Z]{2}[A-Z0-9]{10})", href)
                isin = isin_match.group(1) if isin_match else None
            else:
                nome = cells[0].text.strip().upper()
                isin = None

            prezzo = cells[1].text.strip() if len(cells) > 1 else None

            self.data.append((isin, nome, prezzo))

        return self.data