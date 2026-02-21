import pandas as pd
import sqlite3

# 1. CSV Load karein
data = pd.read_csv("creditcard.csv")

# 2. Sirf wahi columns lein jo hamari database table mein hain
# Hum first 50 rows le rahe hain taaki database bohot heavy na ho jaye
df_subset = data[['Amount', 'V1', 'V2', 'V3', 'Class']].head(50)

# 3. Database se connect karein
conn = sqlite3.connect("database.db")
cur = conn.cursor()

print("Importing data from CSV to Database...")

for index, row in df_subset.iterrows():
    # Class 1 ko 'Fraud' aur 0 ko 'Normal' mein convert karein
    res = "Fraud" if row['Class'] == 1 else "Normal"
    
    cur.execute("""
        INSERT INTO transactions (amount, v1, v2, v3, result, time) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (row['Amount'], row['V1'], row['V2'], row['V3'], res, "2026-02-21 12:00:00"))

conn.commit()
conn.close()

print("✅ Success! 50 rows imported into database.db")