FROM python:3.10-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the entire application first
COPY . .

# Install dependencies and install the current package in development mode
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && pip install -e .

# Expose the port that the application will run on
EXPOSE 6020

# Command to run the application
CMD ["openbb-api", "--app", "demo_risk/app.py", "--host", "0.0.0.0", "--port", "6020"]