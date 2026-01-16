# === Stage 1: Builder ===
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# === Stage 2: Runtime ===
FROM python:3.11-slim

WORKDIR /app

# Install Tor and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure Tor
RUN echo "SocksPort 0.0.0.0:9050" >> /etc/tor/torrc && \
    echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 0" >> /etc/tor/torrc

# Copy wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Create non-root user for security
RUN useradd -m scraper && chown -R scraper:scraper /app
USER scraper

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MAX_THREADS=12

# Healthcheck for Tor
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip || exit 1

# Entrypoint: Start Tor in background, then run app
CMD ["sh", "-c", "tor & sleep 5 && python -m src.main"]
