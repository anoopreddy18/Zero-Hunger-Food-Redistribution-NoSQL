import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, errors

# -------------------------------------------------------------------------
# 1. ENVIRONMENT CONFIGURATION & DATABASE CONNECTION
# -------------------------------------------------------------------------
# Load environment variables from the .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "zero_hunger_food_db")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Ping database to verify connection
    client.admin.command("ping")
    db = client[DB_NAME]
    if "mongodb+srv" in MONGO_URI:
        print(">>> Successfully connected to MongoDB Atlas Cloud Database!")
    else:
        print(">>> Successfully connected to Local MongoDB Server!")
except errors.ServerSelectionTimeoutError as e:
    print(f"[Error] Failed to connect to MongoDB using URI: {MONGO_URI}")
    print("Verify your connection string in .env and your network/IP whitelist access.")
    sys.exit(1)

# Collections
donations_col = db["food_donations"]
shelters_col = db["shelters"]
claims_col = db["claims"]
feedback_col = db["feedback"]

# -------------------------------------------------------------------------
# 2. DATABASE INITIALIZATION & SEED SETUP
# -------------------------------------------------------------------------
def setup_database():
    """Initializes indexes and seed records if collections are empty."""
    try:
        # Create Indexes for fast lookup and uniqueness
        donations_col.create_index([("status", 1)])
        donations_col.create_index([("category", 1)])
        shelters_col.create_index([("shelter_id", 1)], unique=True)
        claims_col.create_index([("claim_id", 1)], unique=True)

        # Seed initial sample data if the collection is empty
        if donations_col.count_documents({}) == 0:
            sample_donations = [
                {
                    "donation_id": "DON001",
                    "item_name": "Steamed Rice & Lentils",
                    "category": "Prepared Food",
                    "quantity": 40,
                    "donor_name": "Royal Feast Caterers",
                    "status": "Available",
                    "created_at": datetime.now()
                },
                {
                    "donation_id": "DON002",
                    "item_name": "Whole Wheat Loaves",
                    "category": "Bakery",
                    "quantity": 25,
                    "donor_name": "Daily Harvest Bakery",
                    "status": "Available",
                    "created_at": datetime.now()
                },
                {
                    "donation_id": "DON003",
                    "item_name": "Fresh Apples & Oranges",
                    "category": "Fresh Produce",
                    "quantity": 50,
                    "donor_name": "City Green Mart",
                    "status": "Claimed",
                    "created_at": datetime.now()
                }
            ]
            donations_col.insert_many(sample_donations)

        if shelters_col.count_documents({}) == 0:
            sample_shelters = [
                {
                    "shelter_id": "SHL001",
                    "name": "Hope Children Home",
                    "contact": "9876543210",
                    "city": "Phagwara"
                },
                {
                    "shelter_id": "SHL002",
                    "name": "Seva Community Kitchen",
                    "contact": "9123456780",
                    "city": "Jalandhar"
                }
            ]
            shelters_col.insert_many(sample_shelters)

    except Exception as e:
        print("[Warning] Index/seed setup skipped or already exists:", e)

# -------------------------------------------------------------------------
# 3. CRUD & QUERY OPERATIONS
# -------------------------------------------------------------------------
def get_all_donations():
    """Retrieve all food donation records."""
    return list(donations_col.find())

def get_available_donations():
    """Retrieve all donations currently marked as Available."""
    return list(donations_col.find({"status": "Available"}))

def get_all_shelters():
    """Retrieve all registered shelters."""
    return list(shelters_col.find())

def insert_shelter(shelter_id, name, contact, city):
    """Add a new shelter/NGO to the database."""
    try:
        shelters_col.insert_one({
            "shelter_id": shelter_id,
            "name": name,
            "contact": contact,
            "city": city
        })
        return True, "Shelter registered successfully."
    except errors.DuplicateKeyError:
        return False, f"Shelter ID '{shelter_id}' already exists."

def insert_donation(donation_id, item_name, category, quantity, donor_name):
    """Post a new surplus food donation."""
    doc = {
        "donation_id": donation_id,
        "item_name": item_name,
        "category": category,
        "quantity": int(quantity),
        "donor_name": donor_name,
        "status": "Available",
        "created_at": datetime.now()
    }
    donations_col.insert_one(doc)
    return True, "Food donation posted successfully."

def claim_donation(donation_id, shelter_id):
    """Link a shelter to a donation and update status to Claimed."""
    target = donations_col.find_one({"donation_id": donation_id})
    if not target:
        return False, "Donation ID not found."
    if target.get("status") != "Available":
        return False, f"Item is already '{target.get('status')}'."

    shelter = shelters_col.find_one({"shelter_id": shelter_id})
    if not shelter:
        return False, "Shelter ID not found. Register shelter first."

    claim_id = f"CLM{claims_col.count_documents({}) + 101}"
    claim_doc = {
        "claim_id": claim_id,
        "donation_id": donation_id,
        "shelter_id": shelter_id,
        "shelter_name": shelter.get("name"),
        "item_name": target.get("item_name"),
        "quantity": target.get("quantity"),
        "status": "Claimed",
        "timestamp": datetime.now()
    }
    claims_col.insert_one(claim_doc)
    donations_col.update_one({"donation_id": donation_id}, {"$set": {"status": "Claimed"}})
    return True, f"Claim successful with Claim ID: {claim_id}"

def update_status(donation_id, new_status):
    """Update delivery lifecycle status of a donation."""
    target = donations_col.find_one({"donation_id": donation_id})
    if not target:
        return False, "Donation record not found."
    valid_statuses = ["Available", "Claimed", "Delivered", "Cancelled"]
    if new_status not in valid_statuses:
        return False, f"Invalid status. Choose from: {', '.join(valid_statuses)}"

    donations_col.update_one({"donation_id": donation_id}, {"$set": {"status": new_status}})
    return True, f"Status updated to '{new_status}' successfully."

def insert_feedback(donation_id, rating, comments):
    """Submit post-delivery feedback."""
    feedback_col.insert_one({
        "donation_id": donation_id,
        "rating": int(rating),
        "comments": comments,
        "submitted_at": datetime.now()
    })
    return True, "Feedback recorded successfully."

# -------------------------------------------------------------------------
# 4. AGGREGATION PIPELINES
# -------------------------------------------------------------------------
def run_aggregation():
    """Run aggregation pipelines for reporting and summary metrics."""
    # Pipeline 1: Group by status to compute total food quantity and counts
    pipeline1 = [
        {"$group": {"_id": "$status", "total_servings": {"$sum": "$quantity"}, "count": {"$sum": 1}}},
        {"$sort": {"total_servings": -1}}
    ]

    # Pipeline 2: Group by category to compute listings count and average quantity
    pipeline2 = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_servings": {"$avg": "$quantity"}}},
        {"$sort": {"count": -1}}
    ]

    return list(donations_col.aggregate(pipeline1)), list(donations_col.aggregate(pipeline2))