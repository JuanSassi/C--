import requests

def fetch_gini(country="Argentina"):
    url = 'https://api.worldbank.org/v2/en/country/all/indicator/SI.POV.GINI?format=json&date=2011:2020&per_page=32500&page=1'
    response = requests.get(url)
    data = response.json()
    for item in data[1]:
        if item["country"]["value"] == country and item["value"] is not None:
            print(item["value"])
            return

if __name__ == "__main__":
    fetch_gini("Argentina")

