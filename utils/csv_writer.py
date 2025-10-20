import csv

def export_recommendations(db):
    recommendations = db.find_recommendations()
    with open("data/recommendations.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "bank", "target_price", "date"])
        # Scrive ogni tupla come una riga nel file
        writer.writerows(recommendations)


def export_stocks(stocks_list):
    with open("data/ftse.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "market_price"])
        for stock in stocks_list:
            writer.writerow([stock[1], stock[2]])
        