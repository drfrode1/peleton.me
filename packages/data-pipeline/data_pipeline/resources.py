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
        
        # Fallback til lokal DuckDB-fil for offline/lokal utvikling (deles med API via LOCAL_DUCKDB_PATH)
        path = os.getenv("LOCAL_DUCKDB_PATH", f"{self.database_name}_local.duckdb")
        return duckdb.connect(path)