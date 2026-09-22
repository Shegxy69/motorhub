# MotorHub

MotorHub is a small full-stack Flask application with a backend API and a frontend web UI for a simple car showroom and cart flow.

## Project structure

- `backend/` — Flask API server
- `frontend/` — Flask app used for the user interface
- `.github/workflows/` — GitHub Actions workflows
- `.gitignore` — ignores Python cache and generated files

## Features

- User sign up and sign in via the backend API
- Showroom catalog of cars with prices
- Add cars to a user cart
- Cart total calculation
- Frontend form-based interaction with the backend

## Requirements

- Python 3
- Flask
- `psycopg2-binary` for the backend database connection

## Local setup

### 1. Create a virtual environment

```bash
cd motorhub
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

Backend:

```bash
cd backend
pip install -r requirements.txt
```

Frontend:

```bash
cd ../frontend
pip install -r requirements.txt
```

## Run the app

### Start the backend

```bash
cd backend
python app.py
```

The backend runs on:

```text
http://localhost:5000
```

### Start the frontend

Open a second terminal and run:

```bash
cd frontend
python app.py
```

The frontend runs on:

```text
http://localhost:8080
```

## API endpoints

### Backend

- `POST /auth` — sign up or sign in a user
- `GET /cars` — return all available cars
- `POST /cart` — add a car to a user's cart
- `GET /cart` — get the current cart and total

## Notes

- The backend currently uses a PostgreSQL connection with default environment values:
  - `DB_HOST=localhost`
  - `DB_USER=postgres`
  - `DB_PASS=password`
- The app is built for local development and can be extended for production deployment.

## GitHub Actions

This project includes CI workflows under `.github/workflows/` to help automate checks for the frontend and backend.
