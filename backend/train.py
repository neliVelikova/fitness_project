import pandas as pd
import joblib

# Load datasets
df1 = pd.read_csv(
    "data/mturkfitbit_export_3.12.16-4.11.16/Fitabase Data 3.12.16-4.11.16/dailyActivity_merged.csv"
)

df2 = pd.read_csv(
    "data/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/dailyActivity_merged.csv"
)

df = pd.concat([df1, df2], ignore_index=True)

df = df.dropna()

# Quick check
print(df.head())
print(df.shape)
print(df.columns)




# =========================
# ANALYTICS SECTION
# =========================

df_activity = df

# Load sleep data (correct path only)
sleep1 = pd.read_csv(
    "data/mturkfitbit_export_3.12.16-4.11.16/Fitabase Data 3.12.16-4.11.16/minuteSleep_merged.csv"
)

sleep2 = pd.read_csv(
    "data/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/minuteSleep_merged.csv"
)

sleep_df = pd.concat([sleep1, sleep2], ignore_index=True)

print("Sleep data preview:")
print(sleep_df.head())

# Summarize sleep per user
sleep_summary = (
    sleep_df.groupby("Id")
    .size()
    .reset_index(name="TotalSleepMinutes")
)

# estimate average daily sleep
sleep_summary["SleepMinutes"] = (
    sleep_summary["TotalSleepMinutes"] / 30
)

sleep_summary = sleep_summary[["Id", "SleepMinutes"]]

print(sleep_summary.head())

# Merge activity + sleep summary
df_final = pd.merge(
    df_activity,
    sleep_summary,
    on="Id",
    how="left"
)

print(df_final.head())
print(df_final.shape)

# =========================
# HEALTH SCORE SYSTEM
# =========================

def calculate_health_score(row):

    score = 0

    # steps
    if row["TotalSteps"] > 10000:
        score += 1

    # sleep
    if row["SleepMinutes"] > 420:
        score += 1

    # active minutes
    if row["VeryActiveMinutes"] > 30:
        score += 1

    # calories
    if row["Calories"] > 2000:
        score += 1

    # final class
    if score >= 3:
        return 2   # healthy
    elif score >= 2:
        return 1   # moderate
    else:
        return 0   # unhealthy


df_final["health_score"] = df_final.apply(
    calculate_health_score,
    axis=1
)

print(df_final[[
    "TotalSteps",
    "SleepMinutes",
    "Calories",
    "health_score"
]].head())

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

X = df_final[[
    "TotalSteps",
    "SleepMinutes",
    "Calories",
    "VeryActiveMinutes"
]]

y = df_final["health_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

print("Accuracy:", model.score(X_test, y_test))


joblib.dump(model, "model.pkl")

# Basic stats
print(df_final[[
    "TotalSteps",
    "Calories",
    "SedentaryMinutes",
    "SleepMinutes"
]].describe())

# Correlation (IMPORTANT for report)
print("\nCorrelation matrix:")
print(df_final[[
    "TotalSteps",
    "Calories",
    "VeryActiveMinutes",
    "SedentaryMinutes",
    "SleepMinutes"
]].corr())

df_final.to_csv("final_dataset.csv", index=False)
