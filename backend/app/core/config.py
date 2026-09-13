from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./movie_platform.db"
    secret_key: str = "change_this_to_a_random_secret_string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    tmdb_api_key: str = ""
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
