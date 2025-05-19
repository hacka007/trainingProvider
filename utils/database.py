import motor.motor_asyncio

from utils.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client["training_provider_app"]

users_collection = db["users"]
roles_collection = db["roles"]
tokens_collection = db["revoked_tokens"]
trainings_collection = db["trainings"]
training_dates_collection = db["training_dates"]
bookings_collection = db["bookings"]
