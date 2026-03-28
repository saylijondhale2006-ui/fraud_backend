from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Load model
model = joblib.load("fraud_model_simple.pkl")

# MongoDB connection
client = MongoClient("mongodb+srv://sayli:sayli123@cluster0.m4jitgt.mongodb.net/")
db = client["fraudDB"]
collection = db["transactions"]

@app.route('/')
def home():
    return "Backend is running"

# 🔹 Predict API
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        amount = float(data.get("amount"))
        time = float(data.get("time"))

        # 🔥 YOUR CUSTOM LOGIC (MAIN CHANGE)
        if amount > 100000:
            risk_score = 0.9

        elif amount > 50000 and time < 10000:
            risk_score = 0.8   # high amount + early time

        elif amount > 50000:
            risk_score = 0.6

        elif amount > 10000:
            risk_score = 0.3

        elif time < 5000:
            risk_score = 0.2

        else:
            risk_score = 0.05

        fraud = risk_score > 0.15

        # Save to database
        collection.insert_one({
            "amount": amount,
            "time": time,
            "risk_score": float(risk_score)
        })

        return jsonify({
            "risk_score": float(risk_score),
            "fraud": bool(fraud)
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)})

# 🔹 Get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    data = []

    for item in collection.find():
        data.append({
            "amount": item["amount"],
            "time": item["time"],
            "risk_score": item["risk_score"]
        })

    return jsonify(data)

# Run server
if __name__ == '__main__':
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)