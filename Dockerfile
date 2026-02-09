FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY src/ src/
COPY config/ config/

# Create user for security
RUN useradd -m gloaks
USER gloaks

# Expose API port
EXPOSE 8000

# Default command (API mode)
# Can be overridden to run CLI: "gloaks scan ..."
CMD ["uvicorn", "gloaks.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
