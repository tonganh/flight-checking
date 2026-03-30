import asyncio
import datetime
from scraper import get_cheapest_flights_in_range
from notifier import format_flights_message, send_telegram_message

async def main():
    print("Flight Tracker Bot Starting...")
    
    # Calculate today and end of year
    today = datetime.datetime.now()
    end_of_year = datetime.datetime(today.year, 4, 12)
    
    print(f"Tracking flights from {today.strftime('%Y-%m-%d')} to {end_of_year.strftime('%Y-%m-%d')}...")
    print("This may take up to 3-5 minutes depending on the remaining days in the year...")
    
    try:
        # bne_han_flights = await get_cheapest_flights_in_range("Brisbane", "Hanoi", today, end_of_year)
        bne_han_flights = await get_cheapest_flights_in_range("Brisbane", "HongKong", today, end_of_year)
    except Exception as e:
        print(f"Failed to scrape flights: {e}")
        bne_han_flights = []
        
    message = format_flights_message(bne_han_flights, today.strftime('%Y-%m-%d'))
    
    send_telegram_message(message)
    
    print("Flight Tracker Bot Finished successfully.")

if __name__ == "__main__":
    asyncio.run(main())
