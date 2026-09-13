from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.base import Base
from app.database.session import engine
import app.models  # noqa: F401 - ensures models are registered before create_all

from app.routers import auth, movies, favorites, watchlist, ratings, reviews, search_history, recommendations, admin

app = FastAPI(title="Movie Discovery Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(favorites.router)
app.include_router(watchlist.router)
app.include_router(ratings.router)
app.include_router(reviews.router)
app.include_router(search_history.router)
app.include_router(recommendations.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
