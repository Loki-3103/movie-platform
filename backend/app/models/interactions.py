from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


# Design note: we never store full TMDb movie data. We only store the
# tmdb_movie_id (the source of truth is always TMDb) plus a small denormalized
# snapshot (title, poster_path) so list views don't need an extra TMDb call
# per row. Full details are always fetched live from TMDb by id.

class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "tmdb_movie_id", name="uq_user_favorite"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tmdb_movie_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    poster_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorites")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "tmdb_movie_id", name="uq_user_watchlist"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tmdb_movie_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    poster_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="watchlist_items")


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("user_id", "tmdb_movie_id", name="uq_user_rating"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tmdb_movie_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # 1.0 - 10.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="ratings")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tmdb_movie_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="search_history")
