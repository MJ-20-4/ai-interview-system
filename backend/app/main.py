from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import check_database_connection
from app.routes.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    is_connected = await check_database_connection()

    if is_connected:
        print("Connected to MongoDB")
    else:
        print("Warning: MongoDB connection failed")

    yield


app = FastAPI(
    title="AI Interview System API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)


@app.get("/")
async def root():
    return {
        "message": "AI Interview System API is running"
    }


@app.get("/health")
async def health_check():
    db_connected = await check_database_connection()

    return {
        "status": "ok" if db_connected else "degraded",
        "mongodb_connected": db_connected
    }
