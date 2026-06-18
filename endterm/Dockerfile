FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install dependencies first to leverage caching
# Copy pyproject.toml and potential lock file
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --no-dev --frozen || uv sync --no-dev

# Copy the rest of the application
COPY src/ .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Environment variables
ENV PYTHONPATH=/app/src
ENV DATABASE_URL=sqlite:////db/events.db

# Healthcheck
#HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  # CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["/app/.venv/bin/python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
