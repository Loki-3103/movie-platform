import httpx
from fastapi import HTTPException
from app.core.config import settings

# Single wrapper around TMDb. Every route that needs movie data goes through
# this file. If TMDb's API ever changes, this is the only place we touch.

BASE_URL = settings.tmdb_base_url
PLACEHOLDER_KEY = "your_tmdb_api_key_here"


async def _get(path: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = settings.tmdb_api_key
    if not settings.tmdb_api_key or settings.tmdb_api_key == PLACEHOLDER_KEY:
        raise HTTPException(
            status_code=500,
            detail="TMDB_API_KEY is not set. Add a valid key to backend/.env (https://www.themoviedb.org/settings/api).",
        )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}{path}", params=params)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach TMDb: {exc}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Movie not found")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"TMDb API request failed ({response.status_code})")
    return response.json()


async def search_movies(query: str, page: int = 1) -> dict:
    return await _get("/search/movie", {"query": query, "page": page})


async def get_popular(page: int = 1) -> dict:
    return await _get("/movie/popular", {"page": page})


async def get_trending(time_window: str = "week") -> dict:
    return await _get(f"/trending/movie/{time_window}")


async def get_top_rated(page: int = 1) -> dict:
    return await _get("/movie/top_rated", {"page": page})


async def get_upcoming(page: int = 1) -> dict:
    return await _get("/movie/upcoming", {"page": page})


async def get_movie_details(movie_id: int) -> dict:
    return await _get(f"/movie/{movie_id}", {"append_to_response": "credits,videos,similar"})


async def get_genres() -> dict:
    return await _get("/genre/movie/list")
