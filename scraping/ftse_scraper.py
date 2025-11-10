import requests
from bs4 import BeautifulSoup
import re

class FTSEScraper:
   
    def __init__(self):
        '''
        Metodo: __init__
        Costruttore della classe FTSEScraper. Inizializza URL, headers e la lista dati.
        Parametri formali:
        None
        Valore di ritorno:
        None -> Nessun valore di ritorno.
        '''
        self.url = "https://www.borse.it/quotazioni/paniere/borsa-italiana/ITA-40"
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        self.data = []

    def fetch(self) -> list:
        '''
        Funzione: fetch
        Esegue lo scraping dei dati (ISIN, nome, prezzo) dei titoli FTSE MIB dal sito borse.it.
        Parametri formali:
        None
        Valore di ritorno:
        list -> Restituisce self.data, una lista di tuple (isin, nome, prezzo) per ogni titolo.
        '''
        response = requests.get(self.url, headers=self.headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser") #creo oggetto di tipo BeautifulSoup passando come parametri al costruttore il testo della risposta e il tipo di parser
        rows = soup.find("tbody").find_all("tr")

        self.data = []
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            # Nome e ISIN
            link = cells[0].find("a") #Prende la prima cella della riga e cerca al suo interno un tag link
            if link:
                nome = link.text.strip().upper() #Estrae il nome dell'azione (es. "ENEL"), rimuove spazi bianchi inutili all'inizio o alla fine e lo converte in maiuscolo.
                href = link.get("href", "") #Prendo l'URL del link
                #Usa un'espressione regolare per cercare un codice ISIN all'interno dell'URL.
                isin_match = re.search(r"([A-Z]{2}[A-Z0-9]{10})", href)
                isin = isin_match.group(1) if isin_match else None #se trova la corrispondenza lo estrae e lo salva 
            else:
                nome = cells[0].text.strip().upper()
                isin = None

            prezzo = cells[1].text.strip() if len(cells) > 1 else None #estraggo il prezzo se c'è una seconda cella, tolgo spazi e lo salvo

            self.data.append((isin, nome, prezzo))

        return self.data