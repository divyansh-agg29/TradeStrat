# TradeStrat Setup Guide

This guide explains how to set up and run the **TradeStrat** application in a local development environment or using Docker.

---

# Prerequisites

Before starting, ensure the following software is installed on your system:

* Python 3.11 or later
* Git
* Docker Desktop *(optional, for containerized execution)*
* Internet connection (required for downloading market data from Yahoo Finance)

You can verify your Python installation by running:

```bash
python --version
```

---

# Clone the Repository

Clone the repository and navigate into the project directory.

```bash
git clone https://github.com/divyansh-agg29/TradeStrat.git

cd TradeStrat
```

---

# Create a Virtual Environment

It is recommended to use a virtual environment to isolate project dependencies.

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Once activated, your terminal should indicate that the virtual environment is active.

---

# Install Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

TradeStrat supports separate Development and Production configurations through environment variables.

Typical variables include:

| Variable    | Description                                             |
| ----------- | ------------------------------------------------------- |
| APP_ENV   | Application environment (`development` or `production`) |
| PORT        | Port on which the application runs (default: 5000)                      |

Example (Windows)

```bash
set APP_ENV=development
set PORT=5000
```

Example (Linux/macOS)

```bash
export APP_ENV=development
export PORT=5000
```

If these variables are not supplied, the application will use its default configuration.

---

# Running the Application

Start the Flask application.

```bash
python app.py
```

or

```bash
flask run
```

depending on your preferred workflow.

The application should now be available at

```
http://localhost:5000
```

---

# Verify Installation

Open your browser and navigate to:

```
http://localhost:5000
```

You should see the TradeStrat application.

You can also verify the health endpoint:

```
GET /health
```

Expected response:

```json
{
    "success": True,
    "data": {
        "status": "healthy",
    },
}
```

---

# Running with Docker

Build the Docker image.

```bash
docker build -t tradestrat .
```

Run the container.

```bash
docker run -p 5000:5000 tradestrat
```

The application will now be available at:

```
http://localhost:5000
```

---

# Running Tests

Execute the complete test suite.

```bash
pytest
```

Generate a coverage report.

```bash
pytest --cov
```

---
