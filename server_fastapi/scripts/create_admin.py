import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


async def create_admin():
    """Create admin user from environment variables"""
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/lexibot_db")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_default_database()
        
        # Get admin details from environment
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_name = os.getenv("ADMIN_NAME", "Admin")
        
        if not admin_email or not admin_password:
            print("❌ Error: ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env file")
            return
        
        # Check if admin already exists
        existing_admin = await db.users.find_one({"email": admin_email})
        if existing_admin:
            print(f"✅ Admin user already exists: {admin_email}")
            return
        
        # Hash password
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin document
        admin_doc = {
            "name": admin_name,
            "email": admin_email.lower(),
            "password": hashed_password,
            "role": "admin",
            "isActive": True,
            "profilePicture": None,
            "preferences": {
                "tone": "formal",
                "language": "English"
            },
            "resetPasswordTokenHash": None,
            "resetPasswordExpiresAt": None,
            "isEmailVerified": True,  # Admin is pre-verified
            "emailVerificationTokenHash": None,
            "emailVerificationExpiresAt": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert admin
        result = await db.users.insert_one(admin_doc)
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Name: {admin_name}")
        print(f"   ID: {result.inserted_id}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_admin())
