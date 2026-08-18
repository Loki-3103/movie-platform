from collections import Counter
from sqlalchemy.orm import Session
from app.crud.interactions import list_favorites, list_ratings, list_search_history
from app.services import tmdb

# Design note (important for interviews):
# get_recommendations() is the ONLY function routers ever call. Right now it
# runs a rule-based scoring strategy. Later, this function's body could be
# swapped for "call a trained model" without changing any router or schema,
# because the function's signature (user -> list of movie dicts) stays the
# same. This is the Strategy pattern - the caller doesn't know or care how
# recommendations are produced internally.


async def get_recommendations(db: Session, user_id: int, limit: int = 20) -> list[dict]:
    favorites = list_favorites(db, user_id)
    ratings = list_ratings(db, user_id)
    history = list_search_history(db, user_id, limit=10)

    # Seed movies: favorites + highly rated movies (score >= 7) drive "similar to" lookups
    seed_ids = [f.tmdb_movie_id for f in favorites]
    seed_ids += [r.tmdb_movie_id for r in ratings if r.score >= 7]
    seed_ids = list(dict.fromkeys(seed_ids))[:5]  # dedupe, cap fan-out to TMDb

    candidates: dict[int, dict] = {}
    genre_votes: Counter = Counter()

    for movie_id in seed_ids:
        details = await tmdb.get_movie_details(movie_id)
        for genre in details.get("genres", []):
            genre_votes[genre["id"]] += 1
        for similar in details.get("similar", {}).get("results", []):
            candidates[similar["id"]] = similar

    # Cold start: no favorites/ratings yet -> fall back to popular movies
    if not candidates:
        popular = await tmdb.get_popular()
        for movie in popular.get("results", []):
            candidates[movie["id"]] = movie

    # Score candidates: reward genre overlap with the user's taste, and
    # nudge by TMDb's own vote_average as a quality signal.
    scored = []
    for movie in candidates.values():
        genre_score = sum(genre_votes.get(g, 0) for g in movie.get("genre_ids", []))
        quality_score = movie.get("vote_average", 0) / 10
        total_score = genre_score + quality_score
        scored.append((total_score, movie))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [movie for _, movie in scored[:limit]]
