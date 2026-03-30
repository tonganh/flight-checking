# Global Flight Tracker Bot ✈️

A Python-based Playwright bot that scrapes Google Flights to find the cheapest flights between your specified routes (default: Brisbane to Hanoi) for **every single day from today until the end of the current year**, strictly filtering flights that are **Under 18 Hours**. 

It then compiles a beautifully formatted alert with direct booking links and sends it directly to your Telegram.

## 1. Local Setup

First, initialize your environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Next, configure your Telegram credentials. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```
Fill in the `.env` file with your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. (If you don't know how to get these, talk to `@BotFather` on Telegram to create a bot, and use a tool like `@getmyid_bot` to get your Chat ID).

Run the bot:
```bash
python main.py
```
*(Note: Because it checks every single day of the year in batches, a full run can take up to 3-5 minutes depending on the time of year!)*

## 2. Automation

### Option A: GitHub Actions (Recommended, Free Cloud Hosting)

This repository includes a `.github/workflows/daily_flight_check.yml` file. If you push this folder to a GitHub repository:
1. Go to your repository **Settings** -> **Secrets and variables** -> **Actions**.
2. Add a New Repository Secret: `TELEGRAM_BOT_TOKEN`
3. Add a New Repository Secret: `TELEGRAM_CHAT_ID`

The bot will automatically run every day at 00:00 UTC and send you the compiled flight alerts!

### Option B: Local Cron Job (Your Mac)

If you strictly want to run it from your own laptop, you can set up a `cron` job. Run `crontab -e` and append this line to run it daily at 9:00 AM:
```bash
0 9 * * * cd /Users/anhtn/code/self-project/flight-checking && source venv/bin/activate && python main.py >> cron.log 2>&1
```
