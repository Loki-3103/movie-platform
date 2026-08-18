from sqlalchemy.orm import Session
from app.models.interactions import Favorite, WatchlistItem, Rating, Review, SearchHistory


# ---------- Favorites ----------

def add_favorite(db: Session, user_id: int, tmdb_movie_id: int, title: str, poster_path: str | None):
    existing = db.query(Favorite).filter_by(user_id=user_id, tmdb_movie_id=tmdb_movie_id).first()
    if existing:
        return existing
    fav = Favorite(user_id=user_id, tmdb_movie_id=tmdb_movie_id, title=title, poster_path=poster_path)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def remove_favorite(db: Session, user_id: int, tmdb_movie_id: int) -> bool:
    fav = db.query(Favorite).filter_by(user_id=user_id, tmdb_movie_id=tmdb_movie_id).first()
    if not fav:
        return False
    db.delete(fav)
    db.commit()
    return True


def list_favorites(db: Session, user_id: int):
    return db.query(Favorite).filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()


# ---------- Watchlist ----------

def add_watchlist_item(db: Session, user_id: int, tmdb_movie_id: int, title: str, poster_path: str | None):
    existing = db.query(WatchlistItem).filter_by(user_id=user_id, tmdb_movie_id=tmdb_movie_id).first()
    if existing:
        return existing
    item = WatchlistItem(user_id=user_id, tmdb_movie_id=tmdb_movie_id, title=title, poster_path=poster_path)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_watchlist_item(db: Session, user_id: int, tmdb_movie_id: int) -> bool:
    item = db.query(WatchlistItem).filter_by(user_id=user_id, tmdb_movie_id=tmdb_movie_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def list_watchlist(db: Session, user_id: int):
    return db.query(WatchlistItem).filter_by(user_id=user_id).order_by(WatchlistItem.created_at.desc()).all()


# ---------- Ratings ----------

def upsert_rating(db: Session, user_id: int, tmdb_movie_id: int, score: float):
    rating = db.query(Rating).filter_by(user_id=user_id, tmdb_movie_id=tmdb_movie_id).first()
    if rating:
        rating.score = score
    else:
        rating = Rating(user_id=user_id, tmdb_movie_id=tmdb_movie_id, score=score)
        db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


def list_ratings(db: Session, user_id: int):
    return db.query(Rating).filter_by(user_id=user_id).order_by(Rating.created_at.desc()).all()


# ---------- Reviews ----------

def add_review(db: Session, user_id: int, tmdb_movie_id: int, content: str):
    review = Review(user_id=user_id, tmdb_movie_id=tmdb_movie_id, content=content)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def list_reviews_for_movie(db: Session, tmdb_movie_id: int):
    return db.query(Review).filter_by(tmdb_movie_id=tmdb_movie_id).order_by(Review.created_at.desc()).all()


def list_reviews_by_user(db: Session, user_id: int):
    return db.query(Review).filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()


# ---------- Search History ----------

def add_search_history(db: Session, user_id: int, query: str):
    entry = SearchHistory(user_id=user_id, query=query)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_search_history(db: Session, user_id: int, limit: int = 20):
    return (
        db.query(SearchHistory)
        .filter_by(user_id=user_id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )
