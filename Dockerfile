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

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Pass environment variables
ENV TELEGRAM_API_ID=<21740783>
ENV TELEGRAM_API_HASH=<a5dc7fec8302615f5b441ec5e238cd46>
ENV TELEGRAM_BOT_TOKEN=<7449731680:AAGvJjogn8jHKo385j2LC4F4wE5_X48_Hck>

# Run bot.py when the container launches
CMD ["python", "bot.py", "bot"]
