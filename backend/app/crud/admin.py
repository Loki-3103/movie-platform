from sqlalchemy.orm import Session
from app.models.user import User
from app.models.interactions import Favorite, WatchlistItem, Rating, Review


def list_all_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)  # cascade="all, delete-orphan" on relationships removes their data too
    db.commit()
    return True


def get_platform_stats(db: Session) -> dict:
    return {
        "total_users": db.query(User).count(),
        "total_favorites": db.query(Favorite).count(),
        "total_watchlist_items": db.query(WatchlistItem).count(),
        "total_ratings": db.query(Rating).count(),
        "total_reviews": db.query(Review).count(),
    }
