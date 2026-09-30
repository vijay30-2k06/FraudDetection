# Fraud Detection Rule Engine

A small full-stack transaction assessment and review application. The backend uses FastAPI, SQLAlchemy, SQLite, Pydantic, bcrypt, and JWT. The frontend uses React, Vite, Axios, Bootstrap, and Lucide icons.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- AWS SES configuration only if you want real alert email delivery

## Run Locally

In PowerShell, install and start the backend:

```powershell
Set-Location backend
py -m venv .venv
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Set `SECRET_KEY` in `backend/.env` to a long random value before starting the API. Generate one with:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Then start the API from the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --env-file .env
```

The API is at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`. SQLite creates `backend/fraud_detection.db` on startup. The app seeds these local demo accounts if they do not exist:

| Role | Email | Password |
| --- | --- | --- |
| Customer | `vijay.k.302006@gmail.com` | `123456` |
| Reviewer | `john@gmail.com` | `qwerty` |
| Customer | `ben@gmail.com` | `789456` |
| Customer | `kevin@gmail.com` | `123789` |

These demo credentials are for local development only. Change or remove them before exposing the app outside your machine.

In a second PowerShell terminal, start the frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend calls `http://localhost:8000` by default. Set `VITE_API_BASE_URL` in a local `frontend/.env.local` to use another API URL.

## Fraud Decisions

Each independent strategy contributes its points: amount over 50,000 adds 40; a changed country adds 30. Country comparison uses the most recent transaction for the same customer and account. Scores 0-39 are Safe, 40-69 are Review, and 70-100 are Fraud. Customers see transaction details but not scores or decisions. Reviewers see only pending Review and Fraud transactions, together with that customer's transaction history. Fraud transactions are saved before SES is attempted, so an email outage does not discard a customer transaction.

The transaction form requests browser location permission to prefill the country. Coordinates are sent to BigDataCloud's reverse-geocoding endpoint to resolve the country name. The field remains editable, and customers can enter a country manually if they deny permission or the lookup is unavailable.

## AWS SES

Set `AWS_REGION`, `SES_FROM_EMAIL`, and `SES_REVIEWER_EMAIL` in `backend/.env`. Configure AWS credentials with the standard AWS SDK credential chain (for example, an AWS profile); credentials are intentionally not stored in this project. The SES identity used as the sender must be verified. While an SES account is in its sandbox, the recipient must also be verified. Grant the configured identity permission to call `ses:SendEmail` in that region. If the sender or recipient is unset, email is skipped and the application remains usable locally.

## Tests

Run the backend unit and API tests from the `backend` directory:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -q
```

Build-check the frontend from the `frontend` directory:

```powershell
Set-Location frontend
npm run build
```

## Postman Smoke Test

Use `http://localhost:8000` as the base URL and send JSON requests with `Content-Type: application/json`.

1. `POST /login` with `{"email":"vijay.k.302006@gmail.com","password":"123456"}`. Copy `access_token` from the response.
2. For customer requests, set Authorization to **Bearer Token** and paste that token. `POST /transaction` with `{"account_id":"acct-100","amount":100,"country":"US"}` establishes account history.
3. Submit another transaction for `acct-100` with amount `50001` and country `CA`. The customer response contains transaction details without a score or decision; the reviewer queue shows the 70-point Fraud assessment and the customer's history.
4. `GET /my-transactions` returns only that customer's transaction details. Safe transactions do not appear in `/reviewer/transactions`.
5. Sign in at `POST /login` with `{"email":"john@gmail.com","password":"qwerty"}`; replace the bearer token. Use `PUT /reviewer/review/{id}` or `PUT /reviewer/clear/{id}` to resolve a pending transaction.

## API

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/login` | Public | Sign in and receive a JWT |
| POST | `/transaction` | Customer | Assess and store a transaction |
| GET | `/my-transactions` | Customer | List the signed-in customer's transactions |
| GET | `/reviewer/transactions` | Reviewer | List pending Review and Fraud transactions |
| PUT | `/reviewer/review/{id}` | Reviewer | Mark a pending transaction Reviewed |
| PUT | `/reviewer/clear/{id}` | Reviewer | Mark a pending transaction Cleared |
