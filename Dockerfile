# Multi-stage build for schemas-demo FastAPI application

FROM python:3.11-slim as builder

# Install system dependencies including protoc
RUN apt-get update && apt-get install -y --no-install-recommends \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY schemas ./schemas/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Generate Protobuf code
RUN protoc --python_out=. --pyi_out=. schemas/user.proto

# Copy application code
COPY app ./app/

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy from builder
COPY --from=builder /app/schemas/ ./schemas/
COPY --from=builder /app/app/ ./app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
