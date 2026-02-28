import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Sample judgments data
SAMPLE_JUDGMENTS = [
    {
        "caseNumber": "2023/SC/001",
        "title": "Muhammad Ali vs State",
        "court": "Supreme Court of Pakistan",
        "judge": "Justice Qazi Faez Isa",
        "dateOfJudgment": datetime(2023, 3, 15),
        "fullText": "This is a sample judgment text for demonstration purposes...",
        "summary": "Case regarding constitutional interpretation of Article 184(3).",
        "keyInformation": {
            "parties": [
                {"name": "Muhammad Ali", "role": "Petitioner"},
                {"name": "State", "role": "Respondent"}
            ],
            "issues": ["Constitutional interpretation", "Fundamental rights"],
            "decisions": ["Petition granted"],
            "deadlines": [],
            "obligations": []
        },
        "caseType": "Constitutional",
        "keywords": ["constitutional law", "fundamental rights", "Article 184"],
        "citations": ["PLD 2023 SC 100"],
        "referencedCases": [],
        "jurisdiction": "Federal",
        "year": 2023,
        "tags": ["constitutional", "landmark"],
        "embedding": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "caseNumber": "2023/LHC/045",
        "title": "XYZ Corporation vs ABC Limited",
        "court": "Lahore High Court",
        "judge": "Justice Ayesha Malik",
        "dateOfJudgment": datetime(2023, 6, 20),
        "fullText": "This judgment concerns a contract dispute between two corporate entities...",
        "summary": "Contract dispute resolved in favor of plaintiff with damages awarded.",
        "keyInformation": {
            "parties": [
                {"name": "XYZ Corporation", "role": "Plaintiff"},
                {"name": "ABC Limited", "role": "Defendant"}
            ],
            "issues": ["Breach of contract", "Damages calculation"],
            "decisions": ["Judgment for plaintiff", "Damages of Rs. 5,000,000 awarded"],
            "deadlines": ["Payment within 60 days"],
            "obligations": ["Defendant to pay damages and costs"]
        },
        "caseType": "Contract",
        "keywords": ["contract", "breach", "damages", "commercial law"],
        "citations": ["2023 CLD 500"],
        "referencedCases": [],
        "jurisdiction": "Punjab",
        "year": 2023,
        "tags": ["contract", "commercial"],
        "embedding": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "caseNumber": "2022/SHC/089",
        "title": "Fatima Bibi vs Muhammad Hassan",
        "court": "Sindh High Court",
        "judge": "Justice Naeemul Haq",
        "dateOfJudgment": datetime(2022, 11, 10),
        "fullText": "This family law case involves custody and maintenance issues...",
        "summary": "Custody granted to mother with visitation rights for father.",
        "keyInformation": {
            "parties": [
                {"name": "Fatima Bibi", "role": "Petitioner"},
                {"name": "Muhammad Hassan", "role": "Respondent"}
            ],
            "issues": ["Child custody", "Maintenance", "Visitation rights"],
            "decisions": ["Custody to mother", "Monthly maintenance Rs. 50,000", "Visitation rights granted"],
            "deadlines": [],
            "obligations": ["Father to pay monthly maintenance"]
        },
        "caseType": "Family",
        "keywords": ["family law", "custody", "maintenance", "divorce"],
        "citations": ["2022 MLD 1200"],
        "referencedCases": [],
        "jurisdiction": "Sindh",
        "year": 2022,
        "tags": ["family", "custody"],
        "embedding": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "caseNumber": "2023/IHC/112",
        "title": "State vs Ahmed Shah",
        "court": "Islamabad High Court",
        "judge": "Justice Athar Minallah",
        "dateOfJudgment": datetime(2023, 1, 25),
        "fullText": "Criminal case involving charges of fraud and misappropriation...",
        "summary": "Defendant convicted on charges of fraud with 5-year sentence.",
        "keyInformation": {
            "parties": [
                {"name": "State", "role": "Prosecution"},
                {"name": "Ahmed Shah", "role": "Accused"}
            ],
            "issues": ["Fraud", "Misappropriation of funds", "Criminal breach of trust"],
            "decisions": ["Guilty verdict", "5 years imprisonment", "Fine of Rs. 1,000,000"],
            "deadlines": ["Appeal within 30 days"],
            "obligations": ["Defendant to serve sentence", "Pay fine"]
        },
        "caseType": "Criminal",
        "keywords": ["criminal law", "fraud", "white collar crime", "conviction"],
        "citations": ["2023 PCrLJ 300"],
        "referencedCases": [],
        "jurisdiction": "Islamabad",
        "year": 2023,
        "tags": ["criminal", "fraud"],
        "embedding": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "caseNumber": "2023/PHC/067",
        "title": "Land Owners Association vs Development Authority",
        "court": "Peshawar High Court",
        "judge": "Justice Qaiser Rashid Khan",
        "dateOfJudgment": datetime(2023, 8, 5),
        "fullText": "Property dispute involving land acquisition and compensation...",
        "summary": "Court orders fair compensation for land acquisition.",
        "keyInformation": {
            "parties": [
                {"name": "Land Owners Association", "role": "Petitioner"},
                {"name": "Development Authority", "role": "Respondent"}
            ],
            "issues": ["Land acquisition", "Compensation", "Due process"],
            "decisions": ["Compensation increased by 40%", "Authority to pay within 90 days"],
            "deadlines": ["Payment within 90 days"],
            "obligations": ["Authority to pay enhanced compensation"]
        },
        "caseType": "Property",
        "keywords": ["property", "land acquisition", "compensation", "eminent domain"],
        "citations": ["2023 PLD 800"],
        "referencedCases": [],
        "jurisdiction": "Khyber Pakhtunkhwa",
        "year": 2023,
        "tags": ["property", "land"],
        "embedding": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

async def seed_judgments():
    """Seed sample judgments into database"""
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/lexibot_db")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_default_database()
        
        print("🌱 Seeding sample judgments...")
        
        # Check if judgments already exist
        count = await db.judgments.count_documents({})
        if count > 0:
            print(f"✅ Database already contains {count} judgments")
            overwrite = input("   Do you want to add more sample judgments? (y/n): ")
            if overwrite.lower() != 'y':
                print("   Seeding cancelled")
                client.close()
                return
        
        # Insert sample judgments
        inserted_count = 0
        for judgment in SAMPLE_JUDGMENTS:
            # Check if this case number already exists
            existing = await db.judgments.find_one({"caseNumber": judgment["caseNumber"]})
            if existing:
                print(f"   ⏭️  Skipping {judgment['caseNumber']} (already exists)")
                continue
            
            result = await db.judgments.insert_one(judgment)
            inserted_count += 1
            print(f"   ✅ Inserted: {judgment['caseNumber']} - {judgment['title']}")
        
        print(f"\n✅ Successfully seeded {inserted_count} new judgments")
        print(f"   Total judgments in database: {await db.judgments.count_documents({})}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error seeding judgments: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(seed_judgments())
