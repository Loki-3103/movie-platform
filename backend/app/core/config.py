from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    tmdb_api_key: str
    tmdb_base_url: str
    frontend_origin: str

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
