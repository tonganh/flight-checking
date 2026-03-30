# Use the official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install cron, tzdata, and other necessary dependencies
RUN apt-get update && apt-get install -y cron tzdata && apt-get clean

# Set the time zone to GMT+7
ENV TZ=Etc/GMT-7
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy the application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its system dependencies (required for browser execution)
RUN playwright install --with-deps chromium

# Copy all source files
COPY . .

# Copy and set up the crontab
COPY crontab /etc/cron.d/flight-bot-cron

# Set permissions and register the crontab
RUN chmod 0644 /etc/cron.d/flight-bot-cron && crontab /etc/cron.d/flight-bot-cron

# Ensure cron logs are visible in Docker logs
RUN touch /var/log/cron.log

# Start cron in the background and tail the log so we can see output in `docker logs`
CMD cron && tail -f /var/log/cron.log
