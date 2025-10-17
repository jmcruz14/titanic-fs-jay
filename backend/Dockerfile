FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app
# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Sync dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY app ./app

EXPOSE 8000

# Run using uv's managed environment
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
