FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for dateutil, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY backend/ .

# Set environment variables (if needed in container)
ENV PYTHONUNBUFFERED=1

# Start the watcher
CMD ["python", "watcher.py"]
