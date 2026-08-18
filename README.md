# Movie Discovery Platform

Full-stack movie discovery app. Movie data comes live from TMDb; the backend
only stores user data (favorites, watchlist, ratings, reviews, search history).

## Prerequisites

- Python 3.10+
- Node.js 18+
- A free TMDb API key: https://www.themoviedb.org/settings/api

## 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `backend/.env` and paste your TMDb API key into `TMDB_API_KEY`.
(The default `.env` uses SQLite, so no database installation is needed.)

Run it:

```bash
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

## 2. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

## 3. Make yourself an admin (optional)

After registering an account, promote it to admin so you can access `/admin`:

```bash
cd backend
sqlite3 movie_platform.db "UPDATE users SET is_admin = 1 WHERE email = 'your@email.com';"
```

Log out and back in on the frontend - an "Admin" link will appear in the navbar.

## 4. Try it

1. Open `http://localhost:5173`
2. Register an account
3. Search a movie, favorite it, rate it
4. Visit "For You" to see recommendations build up as you interact

## Project structure

```
backend/    FastAPI app (see backend/README.md)
frontend/   React + Vite app (see frontend/README.md)
```

We'll cover Docker and deployment in later modules of our conversation.
