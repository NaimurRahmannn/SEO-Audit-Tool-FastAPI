# SEO Audit Tool

## Overview

_TODO: Describe what the SEO Audit Tool does._ A web application that audits a
given URL for SEO issues. This repository is a monorepo containing a FastAPI
backend and a Next.js frontend. No audit logic is implemented yet — this is the
initial scaffold.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Alembic, httpx,
  BeautifulSoup4, Pydantic / pydantic-settings, PostgreSQL (psycopg)
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
- **Tooling:** ruff + black (backend), ESLint + Prettier (frontend)
- **Infra:** Docker, Docker Compose, PostgreSQL

## Project Structure

```
.
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py     # FastAPI app instance, CORS, /health
│   │   └── config.py   # pydantic-settings configuration
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/           # Next.js application
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx    # Landing page with URL input form
│   │   └── globals.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml  # backend + frontend + postgres
├── .env.example
└── README.md
```

## Local Setup

### With Docker Compose (recommended)

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Build and start all services
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000 (health check: http://localhost:8000/health)
- Postgres: localhost:5432

### Running apps individually

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Environment Variables

| Variable                   | App      | Description                                  |
| -------------------------- | -------- | -------------------------------------------- |
| `DATABASE_URL`             | backend  | PostgreSQL connection string (SQLAlchemy)    |
| `PSI_API_KEY`              | backend  | Google PageSpeed Insights API key (optional) |
| `FRONTEND_ORIGIN`          | backend  | Allowed CORS origin for the frontend         |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | Base URL the browser uses to reach the API   |

See [.env.example](.env.example) for placeholder values.

## Architecture

_TODO: Fill in as the system grows._

- The **frontend** collects a URL and calls the backend API.
- The **backend** fetches and analyzes the target page (httpx + BeautifulSoup),
  optionally enriches with PageSpeed Insights data, and persists results in
  PostgreSQL via SQLAlchemy (migrations managed with Alembic).
