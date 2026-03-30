import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse
import re
import datetime

def parse_duration(duration_str):
    # parses "13 hr 10 min" or "15 hr" into minutes
    hr_match = re.search(r'(\d+)\s*hr', duration_str)
    min_match = re.search(r'(\d+)\s*min', duration_str)
    
    hours = int(hr_match.group(1)) if hr_match else 0
    minutes = int(min_match.group(1)) if min_match else 0
    return hours * 60 + minutes

async def fetch_flights_for_date(context, origin, destination, date_str):
    page = await context.new_page()
    
    query = f"Flights to {destination} from {origin} on {date_str} one-way"
    url = "https://www.google.com/travel/flights?q=" + urllib.parse.quote(query)
    
    try:
        await page.goto(url)
        # We wait 4 seconds for flights to load, this minimizes execution time while allowing Google Flights to render
        await page.wait_for_timeout(4000) 
        html = await page.content()
    except Exception as e:
        print(f"[{date_str}] Error: {e}")
        await page.close()
        return []
        
    await page.close()
    
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("li")
    
    flights = []
    
    for li in items:
        text = li.get_text(separator=" | ", strip=True)
        if text and ("AM" in text or "PM" in text) and "$" in text:
            parts = text.split(" | ")
            if len(parts) > 10:
                try:
                    prices = re.findall(r'\$\d+(?:,\d+)?', text)
                    if not prices:
                        continue
                    price_str = prices[0]
                    price_val = int(price_str.replace('$', '').replace(',', ''))
                    
                    airline = "Unknown"
                    for part in parts:
                        if " hr " in part and (" min" in part or len(part.strip()) < 10):
                            idx = parts.index(part)
                            if idx > 0:
                                airline = parts[idx-1]
                            break
                    
                    stops = "Non-stop"
                    for part in parts:
                        if "stop" in part.lower():
                            stops = part
                            break
                    
                    duration = "Unknown"
                    for part in parts:
                        if " hr " in part:
                            duration = part
                            break
                            
                    duration_mins = parse_duration(duration)
                    
                    # USER REQUEST: maximum 18 hours (1080 minutes)
                    if duration_mins <= 1080:
                        flights.append({
                            "date": date_str,
                            "price": price_str,
                            "price_val": price_val,
                            "airline": airline,
                            "stops": stops,
                            "duration": duration,
                            "duration_mins": duration_mins,
                            "link": url
                        })
                except Exception as e:
                    pass
    
    return flights

async def get_cheapest_flights_in_range(origin, destination, start_date, end_date):
    print(f"Scraping flights from {origin} to {destination} between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}...")
    
    # Generate list of dates
    date_list = []
    curr = start_date
    while curr <= end_date:
        date_list.append(curr.strftime('%Y-%m-%d'))
        curr += datetime.timedelta(days=1)
        
    print(f"Total days to check: {len(date_list)}")
    
    all_flights = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-AU",
            timezone_id="Australia/Brisbane"
        )
        
        # Process in batches of 5 to not overwhelm Google and avoid memory crashes
        batch_size = 5
        for i in range(0, len(date_list), batch_size):
            batch = date_list[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(date_list)-1)//batch_size + 1}: {batch}")
            tasks = [fetch_flights_for_date(context, origin, destination, d) for d in batch]
            results = await asyncio.gather(*tasks)
            
            for res in results:
                all_flights.extend(res)
                
        await browser.close()
        
    # Sort and remove duplicates based on purely the exact same flight
    unique_flights = []
    seen = set()
    
    for f in all_flights:
        key = f"{f['date']}-{f['price_val']}-{f['airline']}-{f['stops']}-{f['duration']}"
        if key not in seen:
            seen.add(key)
            unique_flights.append(f)
            
    # Group uniquely by month to get the cheapest per month
    flights_by_month = {}
    for f in unique_flights:
        month = f['date'][:7] # Keep "YYYY-MM"
        if month not in flights_by_month:
            flights_by_month[month] = []
        flights_by_month[month].append(f)
        
    best_flights = []
    for month, m_flights in flights_by_month.items():
        # Sort flights in this month by price
        m_flights_sorted = sorted(m_flights, key=lambda x: x['price_val'])
        # Take top 2 cheapest for this month
        best_flights.extend(m_flights_sorted[:2])
        
    # Finally sort the results chronologically
    best_flights = sorted(best_flights, key=lambda x: x['date'])
    
    return best_flights

if __name__ == "__main__":
    # Test for just next 7 days instead of the whole year to verify logic
    start = datetime.datetime.now()
    end = start + datetime.timedelta(days=7)
    
    flights = asyncio.run(get_cheapest_flights_in_range("Brisbane", "Hanoi", start, end))
    print("\n--- TOP CHEAPEST FLIGHTS (< 18 hours) ---")
    for f in flights:
        print(f"{f['date']} | {f['price']} | {f['airline']} | {f['duration']} | {f['stops']}")
        print(f"Link: {f['link']}\n")
