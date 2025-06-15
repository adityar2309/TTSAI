# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies including sqlite3
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Set environment variables
ENV PYTHONPATH=/app:/app/backend
ENV DATABASE_URL=sqlite:////app/data/ttsai.db
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start the application
CMD ["python", "-u", "app.py"] 