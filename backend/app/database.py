import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27018"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "ai_interview"
)

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]


async def check_database_connection() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
