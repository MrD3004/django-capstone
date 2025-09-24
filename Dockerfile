# Use official slim Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required for mysqlclient and other C extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Expose port 8000 for the Django app
EXPOSE 8000

# Run Django using Gunicorn in production mode
CMD ["gunicorn", "news_portal.wsgi:application", "--bind", "0.0.0.0:8000"]



