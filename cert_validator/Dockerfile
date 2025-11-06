# Dockerfile for HIDR Certificate Validator

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY cert_validator/ ./cert_validator/
COPY config.yaml .

# Create non-root user
RUN useradd -m -u 1000 certvalidator && \
    chown -R certvalidator:certvalidator /app

USER certvalidator

# Expose API port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/api/expert/status', timeout=2)"

# Run API server
CMD ["python", "-m", "uvicorn", "cert_validator.api:app", "--host", "0.0.0.0", "--port", "8001"]
