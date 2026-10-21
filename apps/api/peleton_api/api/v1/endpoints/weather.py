from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import duckdb
import polars as pl
from peleton_api.core.database import get_duckdb_connection
from peleton_api.core.config import settings

router = APIRouter()

@router.get("/")
def get_weather_observations(
    location: Optional[str] = Query(None, description="Optional location ID or name filter (e.g., Forus, SN39040)"),
    days: Optional[int] = Query(7, description="Number of days of history to retrieve", ge=1, le=365),
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

        # ✅ Execute query and fetch directly as a Polars DataFrame
        df: pl.DataFrame = con.execute(query, params).pl()
        
        if df.is_empty() and location:
            raise HTTPException(
                status_code=404, 
                detail=f"Ingen værdata funnet for lokasjon ID '{location}'."
            )

        return {
            "count": len(df),
            "filters": {"location": location, "days": days, "limit": limit},
            "data": df.to_dicts() # ✅ Convert Polars DataFrame to records
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")