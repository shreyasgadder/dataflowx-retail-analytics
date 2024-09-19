db = db.getSiblingDB('retail_db');
db.transactions.createIndex({ "transaction_id": 1 }, { unique: true });