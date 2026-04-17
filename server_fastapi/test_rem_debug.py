import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from bson import ObjectId

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_default_database()
    reminders = await db.reminders.find({}).to_list(None)
    for r in reminders:
        print(f"Title: {r.get('title')}, Due: {r.get('dueDate')}, Notified: {r.get('notificationSent')}, NotifyBefore: {r.get('notifyBeforeDays')}")

if __name__ == "__main__":
    asyncio.run(main())
