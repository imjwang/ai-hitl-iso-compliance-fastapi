# Use Python 3.12-slim as the base image to match project requirements
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install curl and Poetry
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && mv /root/.local/bin/poetry /usr/local/bin/

# Copy pyproject.toml and poetry.lock to install dependencies
COPY pyproject.toml poetry.lock /app/

# Install dependencies without dev dependencies and without creating a virtual environment
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . /app

# Expose the port that FastAPI will use
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
