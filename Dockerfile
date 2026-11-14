# Use the official Python runtime as the base image.
FROM python:3.13-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the dependency list first.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Set production environment by default.
ENV APP_ENV=production

# Create a non-root user for running the application.
RUN adduser --disabled-password --gecos "" appuser

# Copy the rest of the application source code.
COPY --chown=appuser:appuser . .

# Ensure appuser owns the working directory (needed to create SQLite DB at runtime).
RUN chown appuser:appuser /app

# Switch to the non-root user.
USER appuser

# Start the application with a production WSGI server.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 --workers ${WEB_WORKERS:-2} app:app"]