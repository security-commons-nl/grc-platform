FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize Reflex (installs npm packages)
RUN reflex init

# Expose ports (frontend + reflex backend)
EXPOSE 3000 8002

# Run Reflex in production mode
CMD ["reflex", "run", "--env", "prod", "--loglevel", "info"]

