# Movie Discovery Platform

# [App is live!](https://reel-find-pearl.vercel.app/)

Built ReelFind, a full-stack movie discovery platform that lets users browse and search movies with live data — posters, ratings, cast, and genres — in a clean, responsive interface.

A key feature is its recommendation system: when a user marks movies as favorites, the platform analyzes those choices and suggests similar movies based on shared genres, cast, and other patterns. This recommendation engine was originally built as a separate project and later merged into ReelFind as a core feature within the same app.
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


## How to Use

1. **Create an account** - click *Sign Up* and register
2. **Find movies** - search from the homepage or browse the Trending / Popular / Top Rated / Upcoming rows
3. **Save movies** - open any movie to add it to *Favorites* or your *Watchlist*
4. **Rate & review** - pick a score or write a review on a movie's page
5. **Get recommendations** - visit *For You*; the more you favorite and rate, the better the suggestions get.
