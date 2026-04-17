import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from bson import ObjectId

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_default_database()
    users = await db.users.find({}).to_list(None)
    for u in users:
        print(f"Role: {u.get('role')}, Email: {u.get('email')}, ID: {u.get('_id')}")

if __name__ == "__main__":
    asyncio.run(main())
