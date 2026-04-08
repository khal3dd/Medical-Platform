import logging
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Collections def
sessions_collection = db["sessions"]

async def check_database_connection():
   
    try:
        await client.admin.command('ping')
        
        await sessions_collection.create_index("session_id", unique=True)
        
        logger.info(f"✅ MongoDB connected and indexed: {settings.MONGODB_DATABASE}")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection/indexing failed: {e}")
        return False