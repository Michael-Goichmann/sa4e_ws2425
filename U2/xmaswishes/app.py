# app.py
from flask import Flask, request, jsonify
from flask import abort
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["xmasdb"]
wishes_collection = db["wishes"]

@app.route("/wishes", methods=["POST"])
def create_wish():
    data = request.json
    if not data or "name" not in data or "wish" not in data:
        abort(400, "Missing 'name' or 'wish' in request body")
    new_wish = {
        "name": data["name"],
        "wish": data["wish"],
        # default status 1
        "status": data.get("status", 1)
    }
    result = wishes_collection.insert_one(new_wish)
    new_wish["_id"] = str(result.inserted_id)
    return jsonify(new_wish), 201

@app.route("/wishes", methods=["GET"])
def get_all_wishes():
    wishes = list(wishes_collection.find())
    for w in wishes:
        w["_id"] = str(w["_id"])
    return jsonify(wishes), 200

@app.route("/wishes/<wish_id>", methods=["GET"])
def get_wish(wish_id):
    try:
        wish = wishes_collection.find_one({"_id": ObjectId(wish_id)})
    except Exception:
        abort(400, "Invalid wish_id format")
    if not wish:
        abort(404, "Wish not found")
    wish["_id"] = str(wish["_id"])
    return jsonify(wish), 200

@app.route("/wishes/<wish_id>", methods=["PUT"])
def update_wish(wish_id):
    data = request.json
    if not data:
        abort(400, "No data provided")
    update_fields = {}
    if "name" in data:
        update_fields["name"] = data["name"]
    if "wish" in data:
        update_fields["wish"] = data["wish"]
    if "status" in data:
        update_fields["status"] = data["status"]

    result = wishes_collection.update_one(
        {"_id": ObjectId(wish_id)},
        {"$set": update_fields}
    )
    if result.matched_count == 0:
        abort(404, "Wish not found")
    updated_wish = wishes_collection.find_one({"_id": ObjectId(wish_id)})
    updated_wish["_id"] = str(updated_wish["_id"])
    return jsonify(updated_wish), 200

@app.route("/wishes/<wish_id>", methods=["DELETE"])
def delete_wish(wish_id):
    result = wishes_collection.delete_one({"_id": ObjectId(wish_id)})
    if result.deleted_count == 0:
        abort(404, "Wish not found")
    return jsonify({"message": "Wish deleted"}), 200

@app.route("/wishes/sync", methods=["GET"])
def get_wishes_sync():
    updated_after = request.args.get("updatedAfter")
    query = {}
    if updated_after:
        # parse Datum
        from datetime import datetime
        try:
            after_date = datetime.fromisoformat(updated_after.replace("Z",""))
            query = {"updatedAt": {"$gt": after_date}}
        except:
            pass

    # e.g. in Mongo: wishes_collection.find(query)
    results = list(wishes_collection.find(query))
    for r in results:
        r["_id"] = str(r["_id"])  # falls du es in JSON schicken willst
    return jsonify(results), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
