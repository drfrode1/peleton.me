import os


class Settings:
    # Table name kept directly in code configuration
    weather_table_name: str = "bronze_weather_met_frost"

    @property
    def database_url(self) -> str:
        url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
        url = url.replace("postgres://", "postgresql://", 1)

        # Inside Docker containers, 'localhost' or '127.0.0.1' points to the container itself.
        # Translate to the Docker network service name 'postgres' if running inside a container.
        if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
            url = url.replace("@localhost:5432", "@postgres:5432").replace("@127.0.0.1:5432", "@postgres:5432")

        return url

    @property
    def duckdb_path(self) -> str:
        """Returns MotherDuck connection string in production, or local file path in dev."""
        token = os.getenv("MOTHERDUCK_TOKEN")
        if token:
            # MotherDuck cloud connection string
            return f"md:?motherduck_token={token}"

        path = os.getenv("LOCAL_DUCKDB_PATH")
        if not path:
            raise RuntimeError("Neither MOTHERDUCK_TOKEN nor LOCAL_DUCKDB_PATH environment variable is set.")
        return path

    @property
    def default_page_limit(self) -> int:
        return int(os.getenv("DEFAULT_PAGE_LIMIT", "100"))

    @property
    def max_page_limit(self) -> int:
        return int(os.getenv("MAX_PAGE_LIMIT", "1000"))

    # --------------------------------------------------------------------------
    # Strava & OAuth Configuration
    # --------------------------------------------------------------------------
    @property
    def strava_client_id(self) -> str:
        return os.getenv("STRAVA_CLIENT_ID", "")

    @property
    def strava_client_secret(self) -> str:
        return os.getenv("STRAVA_CLIENT_SECRET", "")

    @property
    def strava_redirect_uri(self) -> str:
        return os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/api/v1/strava/callback")

    @property
    def strava_token_encryption_key(self) -> str:
        return os.getenv("STRAVA_TOKEN_ENCRYPTION_KEY", "")

    @property
    def frontend_url(self) -> str:
        return os.getenv("FRONTEND_URL", "http://localhost:3000")

    @property
    def neon_auth_url(self) -> str:
        return os.getenv("NEON_AUTH_URL", "")


settings = Settings()
