import asyncio
import motor.motor_asyncio
from datetime import datetime

async def create_matter():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['lexibot_db']
    
    users = await db.users.find().to_list(None)
    if not users:
        print('No users found.')
        return

    for user in users:
        user_id = str(user['_id'])
        email = user.get('email')
        case_doc = {
            'userId': user_id,
            'title': 'Ahmed Family Property Dispute',
            'caseType': 'Civil',
            'description': 'A civil dispute regarding ownership and possession of ancestral property located in Karachi. The plaintiff claims illegal occupation by the defendant after the death of the original owner.',
            'status': 'Active',
            'filingDate': datetime(2024, 3, 12),
            'hearingDate': datetime(2026, 5, 25),
            'deadline': datetime(2027, 3, 12),
            'plaintiff': 'Muhammad Asif Ahmed',
            'defendant': 'Rashid Mehmood',
            'predictedOutcome': None,
            'keyDetails': {
                'obligations': [],
                'deadlines': [],
                'involvedParties': []
            },
            'tags': ['Property', 'Dispute', 'Karachi'],
            'notes': '',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        await db.cases.insert_one(case_doc)
        print(f'Inserted case for user {user_id} - {email}')

asyncio.run(create_matter())
