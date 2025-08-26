import csv, time, sys
from typing import List
import requests
from bs4 import BeautifulSoup

BASE = "https://quotes.toscrape.com"
HEADERS = {
	"User-Agent": "AlloGroomr/1.0 (+https://github.com/allogroomr/allogroomr-scraper)"
}
TIMEOUT = 15
RETRIES = 3
SLEEP_SEC = 1.0 # be polite

def fetch(url: str) -> requests.Response:
	"""GET with simple retry/backoff."""
	backoff = 1
	for attempt in range (1, RETRIES + 1):
		try:
			r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
			if r.status_code in (200, 404): # 404 = stop condition if it happens
				return r
			if r.status_code in (429, 500, 502, 503, 504):
				time.sleep(backoff)
				backoff *= 2
				continue
			# Other unexpected codes: small backoff then retry
			time.sleep(backoff)
			backoff *= 2
		except requests.RequestException:
			time.sleep(backoff)
			backoff *= 2
	raise RuntimeError(f"Failed to fetch after {RETRIES} tries: {url}")

def parse_quotes(html: str) -> List[dict]:
	soup = BeautifulSoup(html, "lxml")
	out = []
	for q in soup.select(".quote"):
		text = q.select_one(".text").get_text(strip=True)
		author = q.select_one(".author").get_text(strip=True)
		tags = ",".join(t.get_text(strip=True) for t in q.select(".tags a.tag"))
		out.append({"quote": text, "author": author, "tags": tags})
	# next page link (if any)
	next_rel = soup.select_one("li.next > a")
	next_href = next_rel["href"] if next_rel else None
	return out, next_href

def run():
	page = 1
	url = BASE
	total = 0
	with open("quotes.csv", "w", newline="", encoding="utf-8") as f:
		w= csv.writer(f)
		w.writerow(["quote", "author", "tags", "page", "url"])
		while True:
			r = fetch(url)
			if r.status_code == 404:
				break
			rows, next_href = parse_quotes(r.text)
			if not rows:
				break
			for row in rows:
				w.writerow([row["quote"], row["author"], row["tags"], page, url])
			total += len(rows)
			print(f"Page {page}: {len(rows)} quotes (total {total}")
			if not next_href:
				break
			url = BASE.rstrip("/") + next_href
			page += 1
			time.sleep(SLEEP_SEC) # polite crawl
	print(f"Done. Wrote {total} rows to quotes.csv")

if __name__ == "__main__":
	try:
		run()
	except Exception as e:
		print(f"Error: {e}", file=sys.stderr)
		sys.exit(1)
