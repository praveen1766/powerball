import cloudscraper
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def parse_draws(url):
    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    
    draws = []
    
    # LotteryPost uses resultsgrid to layout the draws
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
            except:
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

def fetch_and_merge():
    # Load existing data if any
    data_file = 'nj_data.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = {"pick3": [], "pick4": []}
    else:
        data = {"pick3": [], "pick4": []}

    print("Scraping Pick 3...")
    new_pick3 = parse_draws('https://www.lotterypost.com/results/nj/pick3')
    print(f"Got {len(new_pick3)} Pick 3 draws.")
    
    print("Scraping Pick 4...")
    new_pick4 = parse_draws('https://www.lotterypost.com/results/nj/pick4')
    print(f"Got {len(new_pick4)} Pick 4 draws.")
    
    # Merge, keeping unique dates/times
    def merge(existing, new_data):
        seen = {f"{d['date']}_{d['time']}" for d in existing}
        added = 0
        for d in new_data:
            key = f"{d['date']}_{d['time']}"
            if key not in seen:
                existing.append(d)
                seen.add(key)
                added += 1
        # Sort by date descending, then time descending
        existing.sort(key=lambda x: (x['date'], x['time']), reverse=True)
        return added
        
    p3_added = merge(data['pick3'], new_pick3)
    p4_added = merge(data['pick4'], new_pick4)
    
    print(f"Added {p3_added} new Pick 3 draws and {p4_added} new Pick 4 draws.")
    
    data['last_updated'] = datetime.utcnow().isoformat() + "Z"
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    fetch_and_merge()
