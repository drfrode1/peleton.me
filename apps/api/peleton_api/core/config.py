import os


class Settings:
    # Table name kept directly in code configuration
    weather_table_name: str = "bronze_weather_met_frost"

    @property
    def database_url(self) -> str:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL environment variable is missing.")
        return url.replace("postgres://", "postgresql://", 1)

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


settings = Settings()