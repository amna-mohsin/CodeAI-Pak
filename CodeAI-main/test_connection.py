import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(dotenv_path='apikey.env')

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
print(f"Trying to connect to: {MONGO_URI}")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    print(f"✅ Databases: {client.list_database_names()}")
except Exception as e:
    print(f"❌ Connection failed: {e}")