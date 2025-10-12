import csv

def export_recommendations(recommendations):
    with open("data/recommendations.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["company_id", "bank", "target_price", "date"])
        # Scrive ogni tupla come una riga nel file
        writer.writerows(recommendations)


def export_stocks(stocks_list):
    with open("data/ftse.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "market_price"])
        # Scrive ogni tupla come una riga nel file
        writer.writerows(stocks_list)