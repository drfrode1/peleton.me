from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from peleton_api.api.v1.endpoints import companies, users, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 API starting up...")
    yield
    print("🛑 API shutting down...")


app = FastAPI(
    title="peleton.me API",
    description="Backend API for peleton.me",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "peleton-api"}