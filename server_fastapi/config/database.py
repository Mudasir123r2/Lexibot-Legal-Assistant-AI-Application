import sys
import io
# Force UTF-8 output on Windows to prevent emoji/unicode print errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

database = Database()

async def connect_db():
    """Connect to MongoDB"""
    try:
        database.client = AsyncIOMotorClient(settings.MONGO_URI)
        database.db = database.client.get_default_database()
        # Test connection
        await database.client.admin.command('ping')
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise

async def close_db():
    """Close MongoDB connection"""
    if database.client:
        database.client.close()
        print("✅ MongoDB connection closed")

def get_db():
    """Get database instance"""
    return database.db
