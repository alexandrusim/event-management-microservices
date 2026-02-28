import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_DATABASE_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

try:
    client = MongoClient(MONGO_DATABASE_URL)

    client.server_info()
    print("Conexiune MongoDB reusita.")
except Exception as e:
    print(f"Eroare la conexiunea MongoDB: {e}")
    exit()


db = client["client_manager_db"]
collection_clients = db["clients"]