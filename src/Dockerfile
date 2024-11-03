FROM python:3.12-slim

# Set environment variables
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV RESTACK_SDK_TOKEN=${RESTACK_SDK_TOKEN} 
ENV WANDB_API_KEY=${WANDB_API_KEY}

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY ../pyproject.toml ../poetry.lock ./

# Install dependencies using poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
