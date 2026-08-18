# Backend - Movie Discovery Platform API

FastAPI + SQLAlchemy + SQLite (swappable to Postgres via `DATABASE_URL`).

## Structure

```
app/
  core/          config, JWT + password hashing, auth dependency
  database/      SQLAlchemy engine, session, base class
  models/        DB tables: User, Favorite, WatchlistItem, Rating, Review, SearchHistory
  schemas/       Pydantic request/response models
  crud/          raw DB access functions
  services/      business logic: TMDb API wrapper, recommendation engine
  routers/       API endpoints
  main.py        app entrypoint
```

## Data flow

```
Client -> Router -> Service (if business logic/external API needed) -> CRUD -> Database
```

Routers validate input via schemas and return schemas. They never touch
SQLAlchemy directly - that's CRUD's job.

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your TMDB_API_KEY
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Key design decisions

- **We never store TMDb movie data.** Tables only store `tmdb_movie_id` plus
  a small display snapshot (title, poster). Full details are always fetched
  live from TMDb - this keeps our data in sync with TMDb automatically.
- **JWT auth.** `/api/auth/login` returns a token; the frontend sends it as
  `Authorization: Bearer <token>` on every request.
- **Recommendation engine is rule-based today** (genre overlap from
  favorites/high ratings + TMDb's "similar movies"), but it's isolated in
  `services/recommendations.py` behind a single function so it can be
  swapped for an ML model later without touching routers or schemas.
