# Food Finder Backend

A backend service for a food recommendation app built with FastAPI.
The project uses a layered architecture to separate routing, business logic, and data access.

## Project Structure

```plaintext
food-finder-backend/
├── api/
│   ├── main.py                  # FastAPI application entry point
│   ├── controller/              # HTTP routes and router registration
│   ├── handler/                 # Application/business logic
│   ├── repository/              # Data access layer
│   ├── dto/                     # Request and response models
│   ├── tests/                   # API and unit tests
│   └── __init__.py
├── requirements.txt             # Python dependencies
└── README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Server

From the project root:

```bash
cd api
python3 -m uvicorn main:app --reload
```

Server URL: `http://127.0.0.1:8000`

## Run Tests

From the project root:

```bash
cd api
python -m pytest tests
```
