from pymongo import MongoClient
import os

mongo_uri = os.environ.get('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.admin
try:
    result = db.command('ping')
    print(result)
    db.command('ismaster')
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")