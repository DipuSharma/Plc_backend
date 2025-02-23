from pymongo.errors import PyMongoError
from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import setting

client = AsyncIOMotorClient('mongodb://localhost:27018')
db = client[setting.DATABASE_NAME]

message_collection = db["plc_message"]
plc_collection = db["plc_device"]


async def get_session():
    """Provide a transactional scope around a series of operations with MongoDB, using motor's async session support."""
    try:
        async with await client.start_session() as session:
            try:
                # Starting the transaction
                async with session.start_transaction():
                    yield session
            except PyMongoError as e:
                print(f"Transaction failed: {e}")
                raise
    except Exception as e:
        print(f"{e}")
