# Web Scraping Pipeline

A Python web scraping pipeline built for the FlyRank Backend Internship assignment.

The scraper discovers book pages from Books to Scrape, extracts structured data, validates the records, caches downloaded HTML, handles failures, and produces JSON output with a run report.


## Target Classification

### Site

Books to Scrape

https://books.toscrape.com/


### Why This Site?

Books to Scrape is a public sandbox website designed for practicing web scraping.


### Scope

Only the first 3 catalogue pages are collected.

This produces 60 unique book records.


### Site Type

The target is a static HTML website.

The required book data is already present in the HTML returned by the server, so JavaScript rendering or browser automation is not required.


### robots.txt

No robots.txt file was found during the initial target check — the request returned `404 Not Found`.


### Responsible Use

I will not reuse this code on another website without first checking its rules, terms, robots.txt, and access policies.


## Tech Stack

- Python
- Requests
- BeautifulSoup
- Pydantic


## Installation

Clone the repository:

```bash
git clone https://github.com/Mayakandil/web-scraping-pipeline.git
cd web-scraping-pipeline
```

Install the required packages:

```bash
pip install requests beautifulsoup4 pydantic
```


## Run the Scraper

From the project root, run:

```bash
python3 src/main.py
```

The scraper will:

1. Discover book URLs from the first 3 catalogue pages.
2. Fetch each book page or reuse its cached HTML.
3. Extract the required book information.
4. Normalize the extracted data.
5. Validate each record using Pydantic.
6. Save valid records and validation errors.
7. Generate a report describing the run.


## Pipeline

The scraper follows this pipeline:

```text
Catalogue Pages
      ↓
Discover Book URLs
      ↓
Fetch / Cache HTML
      ↓
Extract Raw Data
      ↓
Normalize Data
      ↓
Validate Records
      ↓
Store JSON Output
      ↓
Generate Run Report
```


## Record Schema

Each validated book record contains:

| Field | Type | Description |
|---|---|---|
| `title` | string | Book title |
| `product_url` | string | Absolute URL of the book |
| `price_text` | string | Original price text |
| `price_gbp` | float | Normalized numeric price |
| `availability_text` | string | Availability information |
| `rating_text` | string | Book rating |
| `description` | string or null | Book description |
| `source_page` | string | Catalogue page where the book was discovered |
| `fetched_at` | string | UTC timestamp for when the record was fetched |

The absolute `product_url` is used as the identity of each book.

For example:

```json
{
  "price_text": "£51.77",
  "price_gbp": 51.77
}
```

The original price is preserved while `price_gbp` provides a numeric value that can be sorted and compared.


## URL Discovery

The scraper starts from the first catalogue page and follows the site's own `Next` link.

Only the first 3 catalogue pages are visited.

Relative book URLs are converted into absolute URLs using `urljoin()`.

Duplicate book URLs are removed before extraction.


## Caching

Downloaded HTML pages are stored locally in the `cache/` directory.

Before making a network request, the scraper checks whether that URL has already been cached.

If the page exists in the cache, the stored HTML is reused:

```text
CACHE HIT
```

Otherwise, the page is downloaded:

```text
FETCH
```

The `cache/` directory is excluded from Git using `.gitignore`, so hundreds of cached HTML files are not committed to the repository.


## Politeness Rules

The scraper follows several rules to reduce unnecessary load on the target website:

- Uses a descriptive `User-Agent`.
- Uses a 10-second request timeout.
- Waits 0.5 seconds after a real network request.
- Caches downloaded HTML locally.
- Reuses cached pages instead of requesting them again.
- Retries a timeout once.
- Retries server-side `5xx` errors once.
- Does not retry errors such as `404` or `403`.
- Only collects the pages required for the assignment.


## Validation

Pydantic is used to validate every extracted record before it is stored.

Valid records are written to:

```text
output/books.json
```

Records that fail schema validation are written to:

```text
output/errors.json
```

along with the reason for the validation failure.

The scraper generates the output from the current validated records instead of appending to the previous output.

Therefore, running the scraper multiple times does not create duplicate records.


## Failure Handling

A failure on one book page does not stop the entire scraping run.

Each book is processed separately using exception handling.

If a page fails, the scraper:

1. Logs the failed page.
2. Records the URL and reason for failure.
3. Skips that page.
4. Continues processing the remaining books.

A test using an intentionally invalid book URL confirmed that the scraper could still finish with all 60 valid books while reporting one failed page.


## Retry Rules

Network failures are handled differently depending on the type of error.

For a timeout or server-side `5xx` error, the scraper waits briefly and retries once.

For errors such as:

```text
404 Not Found
403 Forbidden
```

the scraper does not retry because repeating the same request is unlikely to solve the problem.


## Output

A successful run creates:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

### books.json

Contains the validated book records.

The expected result for the current scope is:

```text
60 valid records
```

### errors.json

Contains records that failed Pydantic schema validation together with the reason for failure.

### run-report.json

Contains a summary of the scraping run, including:

- Start time
- Duration
- Pages fetched
- Cache hits
- Valid records
- Invalid records
- Failed pages


## Sample Run Report

A real run of the scraper produces a report in:

```text
output/run-report.json
```

Example structure:

```json
  {
  "start_time": "2026-10-02T09:46:03.766437+00:00",
  "duration_seconds": 0.743252,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}

```

The values above should be replaced with the values from the actual `output/run-report.json` generated by the final run.


## Why No Browser Was Needed

No browser automation was required for this assignment because the data needed by the scraper is already present in the HTML returned by the server.

Tools such as Selenium or Playwright would introduce additional browser startup time, memory usage, dependencies, and complexity without providing useful additional data for this target.

Using normal HTTP requests is therefore simpler and more efficient for this website.


## Ethics

Web scraping should be performed responsibly.

Before scraping a real website:

- Check its `robots.txt`.
- Review its terms and access policies.
- Respect authentication and access restrictions.
- Do not bypass logins, paywalls, or other technical restrictions.
- Use reasonable request rates.
- Cache responses when appropriate.
- Collect only the data that is needed.
- Prefer an official API when one exists and is appropriate.

This project targets Books to Scrape, a sandbox website intended for web scraping practice.


## Project Structure

```text
web-scraping-pipeline/
│
├── src/
│   └── main.py
│
├── output/
│   ├── books.json
│   ├── errors.json
│   └── run-report.json
│
├── .gitignore
└── README.md
```


## Expected Result

Running:

```bash
python3 src/main.py
```

should complete the pipeline and produce 60 validated book records together with the run report.

Expected validation summary:

```text
--- Validation Summary ---
Valid records: 60
Invalid records: 0
```