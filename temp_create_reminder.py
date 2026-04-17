import asyncio
import motor.motor_asyncio
from datetime import datetime

async def create_reminder():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['lexibot_db']
    
    users = await db.users.find().to_list(None)
    
    for user in users:
        user_id = str(user['_id'])
        
        # Find the case ID for 'Ahmed Family Property Dispute'
        case = await db.cases.find_one({
            "userId": user_id,
            "title": "Ahmed Family Property Dispute"
        })
        
        case_id = str(case['_id']) if case else None
        
        reminder_doc = {
            "userId": user_id,
            "caseId": case_id,
            "title": "File Written Statement",
            "description": "Prepare and submit written statement on behalf of defendant. Ensure all supporting property documents and ownership records are attached.",
            "dueDate": datetime(2026, 5, 10, 11, 0, 0),
            "priority": "High",
            "isCompleted": False,
            "completedAt": None,
            "notifyBeforeDays": 1,
            "notificationSent": False,
            "notificationSentAt": None,
            "isRecurring": False,
            "recurrencePattern": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        await db.reminders.insert_one(reminder_doc)
        print(f"Inserted reminder for user {user.get('email')}")

asyncio.run(create_reminder())
