from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib


app = Flask(__name__)
CORS(app)

# Load trained model
model = joblib.load("model.pkl")

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    steps = data["steps"]
    sleep = data["sleep"]
    energy = data["energy"]
    workout = data["workout"]
    sleep = sleep * 60

    # simulate active minutes from workout intensity
    if workout == 2:
        active_minutes = 60
    elif workout == 1:
        active_minutes = 30
    else:
        active_minutes = 5

    # estimate calories
    calories = 1800 + (steps * 0.04)

    # =========================
    # SMART HEALTH SCORE
    # =========================

    score = 0

    # steps
    if steps >= 10000:
        score += 2
    elif steps >= 6000:
        score += 1

    # sleep
    if sleep >= 480:  # 8 hours
        score += 2
    elif sleep >= 360:  # 6 hours
        score += 1
    else:
        score -= 2

    # energy
    if energy >= 7:
        score += 1
    elif energy <= 3:
        score -= 1

    # workout
    if workout == 2:
        score += 2
    elif workout == 1:
        score += 1

    # =========================
    # FINAL HEALTH RESULT
    # =========================

    if score >= 5:
        health_prediction = "Healthy Lifestyle"

    elif score >= 2:
        health_prediction = "Moderate Lifestyle"

    else:
        health_prediction = "Needs Improvement"

    # recommendation system
    recommendations = []

    if sleep < 420:
        recommendations.append("Try improving sleep duration.")

    if steps < 6000:
        recommendations.append("Increase daily movement and walking.")

    if energy < 5:
        recommendations.append("Your energy levels suggest you may benefit from more recovery time.")

    if workout == 0:
        recommendations.append("Add regular exercise to your routine.")

    if len(recommendations) == 0:
        recommendations.append(
            "Your wellness habits look strong. Stay consistent⚡"
        )

    return jsonify({
        "health_prediction": health_prediction,
        "recommendations": recommendations
    })


@app.route("/analytics")
def analytics():

    import os
    import pandas as pd

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "final_dataset.csv")

    df = pd.read_csv(file_path)

    df = df.dropna(subset=["SleepMinutes"])

    # align dataset (IMPORTANT FIX)
    df = df.sample(min(len(df), 500))  # prevent huge crash risk

    return {
        "avg_steps": float(df["TotalSteps"].mean()),
        "avg_calories": float(df["Calories"].mean()),
        "avg_sleep": float(df["SleepMinutes"].mean()),
        "sedentary": float(df["SedentaryMinutes"].mean()),
        "active": float(df["VeryActiveMinutes"].mean()),

        "sleep": df["SleepMinutes"].tolist(),
        "steps": df["TotalSteps"].tolist(),
        "calories": df["Calories"].tolist()
    }

if __name__ == "__main__":
    app.run(debug=True)