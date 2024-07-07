# Use an optimized Python runtime
FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Pass environment variables
ENV TELEGRAM_API_ID=<your_api_id>
ENV TELEGRAM_API_HASH=<your_api_hash>
ENV TELEGRAM_BOT_TOKEN=<your_bot_token>

# Run bot.py when the container launches
CMD ["python", "bot.py", "bot"]
