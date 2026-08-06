# Use the official Python runtime as the base image.
FROM python:3.13-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the dependency list first.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code.
COPY . .

# Start the Flask application.
CMD ["python", "app.py"]