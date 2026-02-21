import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle

print("Loading dataset...")

data = pd.read_csv("creditcard.csv")

# features
X = data[["Amount", "V1", "V2", "V3"]]
Y = data["Class"]

# scale data
scaler = StandardScaler()
X = scaler.fit_transform(X)

print("Training model...")

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=2
)

# balance classes (important)
model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, Y_train)

# save model + scaler
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("✅ Model trained better!")