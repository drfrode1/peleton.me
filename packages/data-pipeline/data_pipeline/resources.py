import os

import duckdb
from dagster import ConfigurableResource


class MotherDuckResource(ConfigurableResource):
    """Handterer tilkobling mot MotherDuck cloud-instansen eller lokal DuckDB."""
    
    database_name: str = "peleton_db"

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        token = os.getenv("MOTHERDUCK_TOKEN")
        
        # Hvis MOTHERDUCK_TOKEN finnes i Doppler/env, kobles det til MotherDuck
        if token:
            return duckdb.connect(f"md:{self.database_name}?token={token}")
        
        # Fallback til lokal DuckDB-fil for offline/lokal utvikling
        return duckdb.connect(f"{self.database_name}_local.duckdb")