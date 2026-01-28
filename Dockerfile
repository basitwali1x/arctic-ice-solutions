FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY backend/pyproject.toml backend/poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main

# Create the expected directory structure for the React SPA
# The backend app/main.py expects ../frontend/dist/
WORKDIR /app/backend
COPY backend/app ./app
COPY frontend/dist ../frontend/dist

# Copy route JSON files needed for customer data import
COPY lake_charles_routes.json smitty_routes.json ./

# Expose port
EXPOSE 8000

# Run the application
# We run from /app/backend so that ../frontend/dist is accessible
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
