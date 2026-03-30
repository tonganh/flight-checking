import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(message: str) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id or bot_token == "your_telegram_bot_token_here":
        print("Telegram credentials not configured. Skipping notification.")
        print("--- Message that would have been sent ---")
        print(message)
        print("-----------------------------------------")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True # To prevent Telegram from filling the chat with link previews
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram notification sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram notification: {e}")
        return False

def format_flights_message(bne_han_flights, date_str):
    message = f"✈️ <b>Global Flight Tracker</b> ✈️\n"
    message += f"📅 <b>Report Generated: {date_str}</b>\n\n"
    
    message += f"<b>Brisbane (BNE) ➡️ Hanoi (HAN) [Under 18 Hours]</b>\n"
    if not bne_han_flights:
        message += "<i>No flights found matching the criteria today.</i>\n\n"
    else:
        for f in bne_han_flights:
            message += f"🗓 <b>{f['date']}</b>\n"
            message += f"💰 <b>{f['price']}</b> | {f['airline']}\n"
            message += f"⏱️ {f['duration']} | 📍 {f['stops']}\n"
            message += f"🔗 <a href='{f['link']}'>Book Here</a>\n\n"
            
    message += f"<i>Searched until End of Year!</i>\n"
    return message
