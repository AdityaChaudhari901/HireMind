from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from app.config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongodb():
    """Connect to MongoDB and create indexes."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    
    # Create indexes for performance
    await create_indexes()
    
    print(f"Connected to MongoDB: {settings.DB_NAME}")


async def close_mongodb_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes for optimized queries."""
    # Users collection
    await db.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("phone", ASCENDING)])
    ])
    
    # Admins collection
    await db.admins.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True)
    ])
    
    # Base questions collection
    await db.base_questions.create_indexes([
        IndexModel([("topic", ASCENDING)]),
        IndexModel([("difficulty", ASCENDING)]),
        IndexModel([("topic", ASCENDING), ("difficulty", ASCENDING)])
    ])
    
    # Question variants collection
    await db.question_variants.create_indexes([
        IndexModel([("question_id", ASCENDING)]),
        IndexModel([("approved", ASCENDING)])
    ])
    
    # Test sessions collection
    await db.test_sessions.create_indexes([
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("test_link_id", ASCENDING)], unique=True),
        IndexModel([("completed", ASCENDING)]),
        IndexModel([("started_at", ASCENDING)])
    ])
    
    # Attempts collection
    await db.attempts.create_indexes([
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("session_id", ASCENDING), ("question_variant_id", ASCENDING)])
    ])
    
    # Test links collection
    await db.test_links.create_indexes([
        IndexModel([("link_id", ASCENDING)], unique=True),
        IndexModel([("expires_at", ASCENDING)])
    ])


def get_database():
    """Get database instance."""
    return db
