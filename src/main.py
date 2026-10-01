import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime , timezone
import hashlib

URL = "https://books.toscrape.com/catalogue/page-1.html"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/Mayakandil/web-scraping-pipeline)"
}


# ==========================================
# STAGE 1: FETCH + CACHE
# ==========================================

def fetch_page(url):

    # Example:
    # page-1.html -> cache/page-1.html
    url_hash = hashlib.sha256(url.encode()).hexdigest()

    cache_file = Path("cache") / f"{url_hash}.html"
    # If we already downloaded this page before,
    # read it from the cache instead of the internet.
    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT: {url}")
        return html

    # Otherwise, fetch it from the website.
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch page. Status code: {response.status_code}"
        )

    response.encoding = response.apparent_encoding

    html = response.text

    # Create cache folder if it doesn't exist.
    cache_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save HTML so we don't need to fetch it again.
    cache_file.write_text(
        html,
        encoding="utf-8"
    )

    print(f"FETCH: {url}")

    # Wait only after a real network request.
    time.sleep(0.5)

    return html


# ==========================================
# STAGE 2: DISCOVER BOOK URLS
# ==========================================

def discover_books(start_url, max_pages=3):

    book_urls = []
    page_url = start_url
    catalogue_pages = 0

    while page_url and catalogue_pages < max_pages:

        print(f"\nCatalogue page: {page_url}")

        # Get the HTML using our Stage 1 fetch/cache system.
        html = fetch_page(page_url)

        # Parse the HTML.
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # Find all book links on the current catalogue page.
        links = soup.select(
            "article.product_pod h3 a"
        )

        # Convert each relative URL into an absolute URL.
        for link in links:

            href = link.get("href")

            if href:
                full_url = urljoin(
                    page_url,
                    href
                )

                book_urls.append({"product_url": full_url, "source_page":page_url})

        catalogue_pages += 1

        # Find the website's own "Next" button.
        next_link = soup.select_one(
            "li.next a"
        )

        if next_link:
            next_href = next_link.get("href")

            page_url = urljoin(
                page_url,
                next_href
            )

        else:
            page_url = None


    # Remove duplicate URLs while keeping their original order.
    unique_books = {}
    for book in book_urls:
        product_url = book["product_url"]
        
        if product_url not in unique_books:
            unique_books[product_url]= book
    unique_books = list(unique_books.values())

    print("\n--- Discovery Summary ---")

    print(
        f"catalogue_pages={catalogue_pages}, "
        f"discovered={len(book_urls)}, "
        f"unique_urls={len(unique_books)}"
    )

    return unique_books



# ==========================================
# STAGE 3 : EXTRACT BOOK INFO
# ==========================================
def extract_book(product_url , source_page):
    html = fetch_page(product_url)
    soup = BeautifulSoup(html , "html.parser")

    #TITLE
    title_element = soup.select_one("div.product_main h1")
    title = title_element.get_text(strip=True)


    #PRICE
    price_element = soup.select_one("div.product_main p.price_color")
    price_text = price_element.get_text(strip=True)


    #AVAILABILTY  
    availability_element = soup.select_one("div.product_main p.availability")
    availability_text = availability_element.get_text( " ",strip=True)


    #RATING
    rating_element = soup.select_one(".star-rating")
    rating_text = None
    if rating_element:
        classes = rating_element.get("class",[])
        for class_name in classes:
            if class_name != "star-rating":
                rating_text = class_name
                break



    #DESCRIPTION
    description_element = soup.select_one("#product_description +p")
    description = None
    if description_element:
        description = description_element.get_text(" ",strip=True)


    #TIME STAMP
    fetched_at = datetime.now(timezone.utc).isoformat()


    # RAW RECORD
    record = {
    "title": title,
    "product_url": product_url,
    "price_text": price_text,
    "availability_text": availability_text,
   "rating_text": rating_text,
    "description": description,
    "source_page": source_page,
    "fetched_at": fetched_at
}

    return record




    


# ==========================================
# RUN
# ==========================================

book_urls = discover_books(
    URL,
    max_pages=3
)
raw_records =[]
for book in book_urls:
    record = extract_book(book["product_url"], book["source_page"])
    raw_records.append(record)


print("\n--- Extraction Summary ---")
print(f"Raw records extracted: {len(raw_records)}")

if raw_records:
    print("\nFirst record:")
    print(raw_records[0])