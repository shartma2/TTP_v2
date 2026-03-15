FROM python:3.11-slim

# Install system deps, Poetry
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

RUN apt-get update && apt-get install -y graphviz

# Set workdir
WORKDIR /app

# Copy dependency manifests first for efficient caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create venv inside project and install deps
RUN poetry config virtualenvs.in-project false \
 && poetry install --no-root

# Copy application code
COPY . .

# Common API port (adjust if your app uses a different one)
EXPOSE 8000

# Start the app via Poetry
# If your entry script is elsewhere, update the path accordingly.
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]