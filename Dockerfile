# Production Dockerfile for Multimodal Attendance & Engagement Agent
FROM python:3.11-slim

# Prevent Python from writing .pyc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Install required system libraries for OpenCV and audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose server port
EXPOSE 5000

# Run with Gunicorn WSGI
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} app:app --workers 1 --threads 4 --timeout 120"]
