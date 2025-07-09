import os
import joblib
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression

# Connect to your SQLite database
conn = sqlite3.connect("db/FleetStat.db")  # Adjust path if needed

# Load trip data from database
df = pd.read_sql_query("SELECT distance, fuel_consumption FROM trip_info", conn)
conn.close()

# Drop any rows with missing data
df = df.dropna()

# Training data
X = df[["distance"]]
y = df["fuel_consumption"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Make sure ml_models/ exists
os.makedirs("ml_models", exist_ok=True)

# Save model
joblib.dump(model, "ml_models/fuel_predictor.pkl")
print("Model trained and saved as ml_models/fuel_predictor.pkl")  # ← Fixed
