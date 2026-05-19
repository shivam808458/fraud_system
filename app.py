from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import pickle
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# admin login
ADMIN_USER = "admin"
ADMIN_PASS = "password123"

# load model
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# database connection
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json.get("features")

    feature_names = ["Amount","V1","V2","V3"]
    raw = pd.DataFrame([[float(x) for x in data]], columns=feature_names)

    scaled = scaler.transform(raw)

    # prediction
    prediction = model.predict(scaled)[0]

    # REAL probability
    prob = model.predict_proba(scaled)[0][1] * 100

    result = "Fraud" if prediction == 1 else "Normal"

    # save to database
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO transactions(amount,v1,v2,v3,result,time)
    VALUES(?,?,?,?,?,?)
    """,(data[0],data[1],data[2],data[3],result,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return jsonify({
        "result": result,
        "probability": round(prob,2)
    })

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    fraud = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE result='Fraud'"
    ).fetchone()[0]

    normal = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE result='Normal'"
    ).fetchone()[0]

    total = fraud + normal

    conn.close()

    # Real fraud percentage
    fraud_percent = round((fraud / total) * 100, 2) if total > 0 else 0

    # Real feature importance from trained model
    importance = [abs(i) for i in model.coef_[0].tolist()]

    return render_template(
        "dashboard.html",
        fraud=fraud,
        normal=normal,
        total=total,
        fraud_percent=fraud_percent,
        importance=importance
    )


# ================= ADMIN PAGE =================
@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("admin.html",data=rows)


# ================= DELETE SINGLE =================
@app.route("/delete/<int:id>", methods=["POST"])
def delete_log(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# ================= DELETE ALL =================
@app.route("/delete_all", methods=["POST"])
def delete_all():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)