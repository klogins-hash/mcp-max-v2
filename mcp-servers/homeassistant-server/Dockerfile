FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir aiohttp[speedups]

# Copy server files
COPY server.py .
COPY server_http.py .

# Set environment variables (will be overridden by Railway)
ENV HOMEASSISTANT_URL=""
ENV HOMEASSISTANT_TOKEN=""
ENV PORT=8080

# Run the HTTP server for Railway
CMD ["python", "server_http.py"]
