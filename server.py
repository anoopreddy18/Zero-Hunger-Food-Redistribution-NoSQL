from flask import Flask, jsonify, request, send_file
import db_operations as dbo

app = Flask(__name__)

# Ensure DB indexes and collections are initialized
dbo.setup_database()

# 1. Route to serve your HTML page
@app.route("/")
def home():
    return send_file("index.html")

# 2. Get all food donations from MongoDB
@app.route("/api/donations", methods=["GET"])
def get_donations():
    donations = dbo.get_all_donations()
    # Convert MongoDB BSON ObjectId & datetime to strings for JSON
    for d in donations:
        d["_id"] = str(d.get("_id"))
        if "created_at" in d:
            d["created_at"] = str(d["created_at"])
    return jsonify(donations)

# 3. Add a new donation to MongoDB
@app.route("/api/donations", methods=["POST"])
def add_donation():
    data = request.json
    d_id = f"DON{dbo.donations_col.count_documents({}) + 1:03d}"
    success, msg = dbo.insert_donation(
        d_id,
        data.get("item_name"),
        data.get("category"),
        data.get("quantity"),
        data.get("donor_name")
    )
    return jsonify({"success": success, "message": msg})

# 4. Get all shelters from MongoDB
@app.route("/api/shelters", methods=["GET"])
def get_shelters():
    shelters = dbo.get_all_shelters()
    for s in shelters:
        s["_id"] = str(s.get("_id"))
    return jsonify(shelters)

# 5. Add a shelter to MongoDB
@app.route("/api/shelters", methods=["POST"])
def add_shelter():
    data = request.json
    s_id = f"SHL{dbo.shelters_col.count_documents({}) + 1:03d}"
    success, msg = dbo.insert_shelter(
        s_id,
        data.get("name"),
        data.get("contact"),
        data.get("city")
    )
    return jsonify({"success": success, "message": msg})

# 6. Get all claims from MongoDB
@app.route("/api/claims", methods=["GET"])
def get_claims():
    claims = list(dbo.claims_col.find())
    for c in claims:
        c["_id"] = str(c.get("_id"))
        if "timestamp" in c:
            c["timestamp"] = str(c["timestamp"])
    return jsonify(claims)

# 7. Claim food in MongoDB
@app.route("/api/claim", methods=["POST"])
def claim_food():
    data = request.json
    success, msg = dbo.claim_donation(data.get("donation_id"), data.get("shelter_id"))
    return jsonify({"success": success, "message": msg})

# 8. Mark claim as delivered in MongoDB
@app.route("/api/deliver", methods=["POST"])
def deliver_food():
    data = request.json
    d_id = data.get("donation_id")
    dbo.update_status(d_id, "Delivered")
    dbo.claims_col.update_one({"donation_id": d_id}, {"$set": {"status": "Delivered"}})
    return jsonify({"success": True, "message": "Marked as Delivered"})

if __name__ == "__main__":
    print(">>> Web app running at http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)