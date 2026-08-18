import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import time
import random
from datetime import datetime, timedelta

SCRAPER = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

def fetch_html(url, retries=3, delay=3):
    """Fetch URL with retry logic."""
    for attempt in range(retries):
        try:
            resp = SCRAPER.get(url, timeout=25)
            if resp.ok:
                return resp.text
            print(f"  HTTP {resp.status_code} for {url}")
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
        if attempt < retries - 1:
            time.sleep(delay)
    return None


def parse_draws_from_page(html):
    """Extract all draw records from a LotteryPost results page."""
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    draws = []

    grid = soup.find('div', class_='resultsgrid')
    if not grid:
        return draws

    for game_div in grid.find_all('div', class_='resultsgame'):
        # The <time> element (day's date) only appears once per game_div, on
        # the first drawing (usually Midday) — Evening's drawing has no <time>
        # of its own, so the date must be shared across all drawings for the day.
        time_el = game_div.find('time')
        if not time_el:
            continue
        date_str = time_el.text.strip()
        try:
            dt = datetime.strptime(date_str, "%A, %B %d, %Y")
            iso_date = dt.strftime("%Y-%m-%dT00:00:00.000")
        except Exception:
            continue

        for draw in game_div.find_all('div', class_='resultsdrawing'):
            tod_el = draw.find('div', class_='TOD')
            time_name = tod_el.text.strip() if tod_el else 'Unknown'

            # First <ul class="resultsnums"> = the winning numbers
            nums_ul = draw.find('ul', class_='resultsnums')
            if not nums_ul:
                continue

            main_nums = [li.text.strip() for li in nums_ul.find_all('li')]
            if main_nums:
                draws.append({
                    "date": iso_date,
                    "time": time_name,
                    "numbers": main_nums
                })
    return draws


def fetch_past_pages(game_slug, months_back=12):
    """
    Fetch historical draws using LotteryPost's /past and /past/YYYY/M URL pattern.
    The /past page shows the current + previous month's results,
    and /past/YYYY/M shows a specific month.
    """
    all_draws = []
    hard_failure = False  # a request for the current month came back completely empty (blocked/down)
    today = datetime.utcnow()

    # Build list of (year, month) tuples to fetch
    months_to_fetch = []
    for m in range(months_back):
        target = today - timedelta(days=30 * m)
        months_to_fetch.append((target.year, target.month))

    # Deduplicate
    months_to_fetch = list(dict.fromkeys(months_to_fetch))

    for year, month in months_to_fetch:
        is_current_month = (year == today.year and month == today.month)
        if is_current_month:
            # Current month: use the /past URL (no date suffix)
            url = f"https://www.lotterypost.com/results/nj/{game_slug}/past"
        else:
            url = f"https://www.lotterypost.com/results/nj/{game_slug}/past/{year}/{month}"

        print(f"  Fetching {game_slug} past results {year}/{month:02d} ...")
        html = fetch_html(url)
        if html is None and is_current_month:
            # The current-month page should always return data — a total fetch
            # failure here almost always means the request was blocked (e.g. by
            # Cloudflare on a datacenter IP), not that there's genuinely nothing.
            print(f"    ⚠️ HARD FAILURE — no response for current-month {game_slug} page")
            hard_failure = True
        draws = parse_draws_from_page(html)
        print(f"    → {len(draws)} draws")
        all_draws.extend(draws)
        time.sleep(1.5 + random.uniform(0, 1.5))  # be polite, add jitter

    return all_draws, hard_failure


def merge_draws(existing, new_data):
    """Merge new draws into existing list, deduplicating by date+time."""
    seen = {f"{d['date']}_{d['time']}" for d in existing}
    added = 0
    for d in new_data:
        key = f"{d['date']}_{d['time']}"
        if key not in seen:
            existing.append(d)
            seen.add(key)
            added += 1
    # Sort newest first. Evening is later in the day than Midday, so within the
    # same date it must sort ahead of Midday — plain string sort on 'time' gets
    # this backwards ("Midday" > "Evening" alphabetically).
    time_rank = {'Evening': 1, 'Midday': 0}
    existing.sort(key=lambda x: (x['date'], time_rank.get(x['time'], 0)), reverse=True)
    return added


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

    # Smart fetch: full history if < 30 records, otherwise last 2 months
    p3_count = len(data.get('pick3', []))
    p4_count = len(data.get('pick4', []))
    months = 12 if (p3_count < 30 or p4_count < 30) else 2

    print(f"Existing: {p3_count} Pick 3, {p4_count} Pick 4. Fetching {months} months.")

    print("\nScraping Pick 3 past results...")
    new_pick3, p3_hard_failure = fetch_past_pages('pick3', months_back=months)
    print(f"Total Pick 3 fetched: {len(new_pick3)}")

    print("\nScraping Pick 4 past results...")
    new_pick4, p4_hard_failure = fetch_past_pages('pick4', months_back=months)
    print(f"Total Pick 4 fetched: {len(new_pick4)}")

    p3_added = merge_draws(data['pick3'], new_pick3)
    p4_added = merge_draws(data['pick4'], new_pick4)

    print(f"\nAdded {p3_added} new Pick 3 and {p4_added} new Pick 4 draws.")
    print(f"Totals: {len(data['pick3'])} Pick 3, {len(data['pick4'])} Pick 4.")

    data['last_updated'] = datetime.utcnow().isoformat() + "Z"

    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved to {data_file}")

    if p3_hard_failure or p4_hard_failure:
        print("\n❌ One or more current-month requests were blocked/failed — "
              "data may be stale. Failing the run so it's visible instead of a silent no-op.")
        return False
    return True


if __name__ == "__main__":
    import sys
    ok = fetch_and_merge()
    sys.exit(0 if ok else 1)
