// Connect to the project database
use zero_hunger_food_db;

// 1. JSON Schema Validation Example for Collections
db.createCollection("food_donations_validated", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["donation_id", "item_name", "quantity", "status"],
         properties: {
            donation_id: { bsonType: "string", description: "Must be a string identifier" },
            item_name: { bsonType: "string", description: "Food name" },
            quantity: { bsonType: "int", minimum: 1, description: "Must be a positive integer" },
            status: { enum: ["Available", "Claimed", "Delivered", "Cancelled"] }
         }
      }
   }
});

// 2. Index Creation
db.food_donations.createIndex({ "status": 1 });
db.food_donations.createIndex({ "category": 1 });
db.shelters.createIndex({ "shelter_id": 1 }, { unique: true });
db.claims.createIndex({ "claim_id": 1 }, { unique: true });

// 3. Aggregation Pipelines
// Summary by status
db.food_donations.aggregate([
  { $group: { _id: "$status", total_servings: { $sum: "$quantity" }, count: { $sum: 1 } } },
  { $sort: { total_servings: -1 } }
]);

// Summary by category
db.food_donations.aggregate([
  { $group: { _id: "$category", total_listings: { $sum: 1 }, avg_quantity: { $avg: "$quantity" } } },
  { $sort: { total_listings: -1 } }
]);