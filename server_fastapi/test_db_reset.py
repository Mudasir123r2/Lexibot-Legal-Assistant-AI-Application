import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from datetime import datetime

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_default_database()
    
    # 1. Reset all notification flags so the system tests again instantly!
    await db.reminders.update_many({}, {"$set": {"notificationSent": False}})
    print("✅ Reset notification flags!")

if __name__ == "__main__":
    asyncio.run(main())