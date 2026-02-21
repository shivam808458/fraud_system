from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import pickle
import sqlite3
from datetime import datetime

app = Flask(__name__)

# 1. Load trained model and scaler
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# Database Helper Function
def save_to_db(amount, v1, v2, v3, result):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (amount, v1, v2, v3, result, time) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (amount, v1, v2, v3, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

# Prediction API with Scaling and Warning Fix
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json["features"]
        
        # 2. Fix UserWarning by using DataFrame with feature names
        feature_names = ["Amount", "V1", "V2", "V3"]
        raw_features = pd.DataFrame([data], columns=feature_names)

        # 3. Scale the features
        scaled_features = scaler.transform(raw_features)

        # 4. Predict
        prediction = model.predict(scaled_features)

        # Handle probability safely
        probability = 0
        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(scaled_features)[0][1] * 100

        result = "Fraud" if prediction[0] == 1 else "Normal"

        # 5. Save record to database for Admin panel
        save_to_db(data[0], data[1], data[2], data[3], result)

        return jsonify({
            "result": result,
            "probability": round(probability, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# Admin Route to view all transactions
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("admin.html", data=rows)

# Dashboard Route for analytics
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    # Get Fraud count
    cur.execute("SELECT COUNT(*) FROM transactions WHERE result='Fraud'")
    fraud_count = cur.fetchone()[0]
    # Get Normal count
    cur.execute("SELECT COUNT(*) FROM transactions WHERE result='Normal'")
    normal_count = cur.fetchone()[0]
    conn.close()
    return render_template("dashboard.html", fraud=fraud_count, normal=normal_count)

if __name__ == "__main__":
    app.run(debug=True)