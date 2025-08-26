# AlloGroomr - Multipage Scraper

A Python scraper that demonstrates how to handle pagination and export results to csv.

**Target site:** [Quotes to Scrape](https://quotes.toscrape.com)
**Tech stack:** Python, Requests, BeautifulSoup, CSV

### Features
- Extracts all quotes, authors, and tags
- Handles multi-page navigation automatically
- Polite crawl with delays and custom User-Agent
- Outputs clean CSV with quote, author, tags, page, and URL

### Run locally
```bash
pip install -r requirements.txt
python quotes_paged.py
