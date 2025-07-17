from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")

# Replace this with a valid MongoDB database name (no spaces)
db = client["arissa_ai"]
collection = db["hotel_profiles"]

def insert_or_update_hotel_profile(data):
    result = collection.update_one(
        {"hotel_id": data["hotel_id"]},
        {"$set": data},
        upsert=True
    )
    return "Updated" if result.matched_count > 0 else str(result.upserted_id)

def get_hotel_profile_by_id(hotel_id):
    return collection.find_one({"hotel_id": hotel_id})

def get_all_hotel_ids():
    return [doc["hotel_id"] for doc in collection.find({}, {"hotel_id": 1})]



