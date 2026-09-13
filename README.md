# Movie Discovery Platform

# [App is live!](https://reel-find-pearl.vercel.app/)

A full-stack movie discovery app. Browse what's trending, search any movie, and
build a personal library of favorites and watchlist items. Movie data comes
live from TMDb; your preferences and activity are stored locally.

## Features

- **Discover movies** - trending this week, popular, top-rated, and upcoming, all live from TMDb
- **Search** - find any movie by title across the full TMDb catalog
- **Movie pages** - trailers, cast, genres, and similar-movie suggestions
- **Personal library** - save movies to your favorites and watchlist
- **Rate & review** - score movies on a 1-10 scale and write reviews
- **For You** - personalized recommendations built from your favorites, ratings, and search history
- **Accounts & admin** - secure sign-up/login with JWT; an admin panel for user management

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, JWT auth
- **Frontend:** React + Vite, Tailwind CSS
- **Data:** SQLite database, live API data from [TMDb](https://www.themoviedb.org)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free TMDb API key: https://www.themoviedb.org/settings/api

### 1. Run the backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` from `.env.example` and paste your TMDb API key:

```
TMDB_API_KEY=your_api_key_here
```

Start the server:

```bash
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000` with interactive docs at
`http://localhost:8000/docs`.

### 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## How to Use

1. **Create an account** - click *Sign Up* and register
2. **Find movies** - search from the homepage or browse the Trending / Popular / Top Rated / Upcoming rows
3. **Save movies** - open any movie to add it to *Favorites* or your *Watchlist*
4. **Rate & review** - pick a score or write a review on a movie's page
5. **Get recommendations** - visit *For You*; the more you favorite and rate, the better the suggestions get

### Make yourself an admin (optional)

To access the admin panel, promote your account after registering:

```bash
cd backend
sqlite3 movie_platform.db "UPDATE users SET is_admin = 1 WHERE email = 'your@email.com';"
```
