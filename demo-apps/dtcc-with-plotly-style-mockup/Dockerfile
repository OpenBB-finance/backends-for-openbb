# DTCC OpenBB Dashboard System - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for fly.io mount
RUN mkdir -p /app/data

# Expose port (Fly.io uses 6020)
EXPOSE 6020

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=6020

# Run the application using PORT environment variable
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6020"]