# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Pass environment variables
ENV TELEGRAM_API_ID=<21740783>
ENV TELEGRAM_API_HASH=<a5dc7fec8302615f5b441ec5e238cd46>
ENV TELEGRAM_BOT_TOKEN=<7496680438:AAHyEZDGnIoARpfywrzQOhB27un9pja49p4>

# Run bot.py when the container launches
CMD ["python", "bot.py", "bot"]
