from pymongo.errors import PyMongoError
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["plc_data"]

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
