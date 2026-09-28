import requests
from pathlib import Path


URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_FILE = Path("cache/catalogue-page-1.html")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/Mayakandil/web-scraping-pipeline)"
}

if CACHE_FILE.exists():
    html = CACHE_FILE.read_text(encoding="utf-8")
    print("CACHE HIT")
else:
    response = requests.get(URL,headers=HEADERS,timeout=10)


    if response.status_code !=200:
        raise Exception(f"failed to fetch page. status code: {response.status_code}")

    html = response.text
    CACHE_FILE.parent.mkdir(parents=True, exist_ok= True )
    CACHE_FILE.write_text(html, encoding="utf-8")
    print("FETCH")
print(f"Response size: {len(html)} characters")