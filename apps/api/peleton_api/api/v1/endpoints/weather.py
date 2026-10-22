
import duckdb
import polars as pl
from fastapi import APIRouter, Depends, HTTPException, Query

from peleton_api.core.config import settings
from peleton_api.core.database import get_duckdb_connection

router = APIRouter()

@router.get("/")
def get_weather_observations(
    location: str | None = Query(None, description="Optional location ID or name filter (e.g., Forus, SN39040)"),
    days: int | None = Query(7, description="Number of days of history to retrieve", ge=1, le=365),
    limit: int = Query(100, ge=1, le=settings.max_page_limit),
    con: duckdb.DuckDBPyConnection = Depends(get_duckdb_connection),
):
    """
    Retrieve weather observations using Polars.
    """
    try:
        query = f"SELECT * FROM {settings.weather_table_name}"
        params = []
        conditions = []

        if location:
            conditions.append("LOWER(location_id) = LOWER(?)")
            params.append(location)

        if days:
            conditions.append("reference_time >= CURRENT_TIMESTAMP - (INTERVAL '1 day' * ?)")
            params.append(days)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY reference_time DESC LIMIT ?"
        params.append(limit)

        # ✅ Execute query and fetch directly as a Polars DataFrame using con.sql()
        df: pl.DataFrame = con.sql(query, params=params).pl()
        
        if df.is_empty() and location:
            raise HTTPException(
                status_code=404, 
                detail=f"No weather data found for location ID '{location}'."
            )

        return {
            "count": len(df),
            "filters": {"location": location, "days": days, "limit": limit},
            "data": df.to_dicts() # ✅ Convert Polars DataFrame to records
        }

    except HTTPException:
        raise
    except duckdb.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e!s}")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}")