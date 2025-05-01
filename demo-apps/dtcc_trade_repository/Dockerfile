FROM python:3.10-slim

WORKDIR /app

# Copy the entire application first
COPY . .

# Install dependencies and install the current package in development mode
RUN pip install -e .

# Expose the port that the application will run on
EXPOSE 6020

# Command to run the application
CMD ["openbb-api", "--app", "openbb_swaps/app/app.py", "--host", "0.0.0.0", "--port", "6020"]