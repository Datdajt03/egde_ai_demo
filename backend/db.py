from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logger = logging.getLogger("backend")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_helper = Database()

def get_database():
    return db_helper.db

def get_collection(name: str):
    if db_helper.db is None:
        raise RuntimeError("Database connection not initialized")
    return db_helper.db[name]

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    try:
        db_helper.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db_helper.db = db_helper.client[settings.DATABASE_NAME]
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    if db_helper.client:
        db_helper.client.close()
        logger.info("MongoDB connection closed.")
