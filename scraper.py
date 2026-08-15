import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime, timedelta

SCRAPER = cloudscraper.create_scraper()

def fetch_html(url, retries=3, delay=2):
    """Fetch a URL with retry logic."""
    for attempt in range(retries):
        try:
            resp = SCRAPER.get(url, timeout=20)
            if resp.ok:
                return resp.text
            print(f"  HTTP {resp.status_code} for {url}")
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
        if attempt < retries - 1:
            time.sleep(delay)
    return None

def parse_draws(url):
    """Parse Pick 3 / Pick 4 results from a LotteryPost results page."""
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    draws = []

    grid = soup.find('div', class_='resultsgrid')
    if not grid:
        return draws

    rows = grid.find_all('div', class_='resultsgame')
    for row in rows:
        drawings = row.find_all('div', class_='resultsdrawing')
        for draw in drawings:
            time_el = draw.find('time')
            if not time_el:
                continue
            date_str = time_el.text.strip()
            try:
                dt = datetime.strptime(date_str, "%A, %B %d, %Y")
                iso_date = dt.strftime("%Y-%m-%dT00:00:00.000")
            except Exception:
                continue

            tod_el = draw.find('div', class_='TOD')
            time_name = tod_el.text.strip() if tod_el else 'Unknown'

            nums_lists = draw.find_all('ul', class_='resultsnums')
            if not nums_lists:
                continue

            main_nums = [li.text.strip() for li in nums_lists[0].find_all('li')]
            if main_nums:
                draws.append({
                    "date": iso_date,
                    "time": time_name,
                    "numbers": main_nums
                })

    return draws

def fetch_calendar_months(game_slug, months_back=12):
    """Fetch multiple months of history from the calendar pages."""
    all_draws = []
    today = datetime.utcnow()

    for m in range(months_back):
        target = today - timedelta(days=30 * m)
        year, month = target.year, target.month
        url = f"https://www.lotterypost.com/results/nj/{game_slug}/calendar/{year}/{month}"
        print(f"  Fetching {game_slug} calendar {year}/{month:02d}…")
        draws = parse_draws(url)
        print(f"    → {len(draws)} draws")
        all_draws.extend(draws)
        time.sleep(1)  # be polite to the server

    return all_draws

def fetch_and_merge():
    data_file = 'nj_data.json'

    # Load existing data
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            try:
                data = json.load(f)
            except Exception:
                data = {"pick3": [], "pick4": []}
    else:
        data = {"pick3": [], "pick4": []}

    # Decide how far back to fetch:
    # If we have very little data, do a full 12-month history pull.
    # Otherwise just grab the last 2 months (incremental).
    p3_count = len(data.get('pick3', []))
    p4_count = len(data.get('pick4', []))
    months = 12 if (p3_count < 30 or p4_count < 30) else 2

    print(f"Existing data: {p3_count} Pick 3, {p4_count} Pick 4 draws. Fetching {months} month(s).")

    print("\nScraping Pick 3…")
    new_pick3 = fetch_calendar_months('pick3', months_back=months)
    print(f"Got {len(new_pick3)} Pick 3 draws total.")

    print("\nScraping Pick 4…")
    new_pick4 = fetch_calendar_months('pick4', months_back=months)
    print(f"Got {len(new_pick4)} Pick 4 draws total.")

    def merge(existing, new_data):
        seen = {f"{d['date']}_{d['time']}" for d in existing}
        added = 0
        for d in new_data:
            key = f"{d['date']}_{d['time']}"
            if key not in seen:
                existing.append(d)
                seen.add(key)
                added += 1
        # Sort newest first
        existing.sort(key=lambda x: (x['date'], x['time']), reverse=True)
        return added

    p3_added = merge(data['pick3'], new_pick3)
    p4_added = merge(data['pick4'], new_pick4)

    print(f"\nAdded {p3_added} new Pick 3 and {p4_added} new Pick 4 draws.")
    print(f"Total now: {len(data['pick3'])} Pick 3, {len(data['pick4'])} Pick 4.")

    data['last_updated'] = datetime.utcnow().isoformat() + "Z"

    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved to {data_file}")

if __name__ == "__main__":
    fetch_and_merge()
