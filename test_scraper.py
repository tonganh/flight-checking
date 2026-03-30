import asyncio
from playwright.async_api import async_playwright
import datetime
import urllib.parse

async def test_google_flights():
    print("Starting Playwright for Google Flights...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-AU",
            timezone_id="Australia/Brisbane"
        )
        page = await context.new_page()
        
        # Search for a flight 7 days from now
        date = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        
        query = f"Flights to Hanoi from Brisbane on {date} one-way"
        url = "https://www.google.com/travel/flights?q=" + urllib.parse.quote(query)
        print(f"Navigating to {url}...")
        
        await page.goto(url)
        # Taking a screenshot of the initial load
        await page.screenshot(path="google_initial.png")
        
        print("Waiting for network idle...")
        await page.wait_for_timeout(10000)
        
        print("Taking final screenshot...")
        await page.screenshot(path="google_after_load.png")
        
        html = await page.content()
        with open("google.html", "w") as f:
            f.write(html)
            
        await browser.close()
        print("Finished.")

if __name__ == "__main__":
    asyncio.run(test_google_flights())
