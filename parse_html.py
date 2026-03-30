from bs4 import BeautifulSoup
import re

with open("google.html", "r") as f:
    html = f.read()
    
soup = BeautifulSoup(html, "html.parser")

# Find all items that look like flights. Usually they have aria-labels containing "Flight from" or similar.
# Or look for spans with prices
items = soup.find_all("li")
print(f"Total list items: {len(items)}")

for li in items:
    text = li.get_text(separator=" | ", strip=True)
    if text and ("AM" in text or "PM" in text) and "$" in text:
        # It's likely a flight element
        print("---")
        print(text)
