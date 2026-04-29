FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY .venv ./.venv

# Copy source
COPY ./ ./

# Ensure static directory exists
RUN mkdir -p /app/static/images

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
