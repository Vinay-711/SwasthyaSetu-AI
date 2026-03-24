"""
SwasthyaSetu AI — Occupational Risk Model Training (MLflow)
Run this notebook in Databricks or locally to train and register the model.
"""

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# ── Configuration ──────────────────────────────────────────────────────────
EXPERIMENT_NAME = "swasthya_occupational_risk"
MODEL_NAME      = "swasthya_risk_model"

mlflow.set_experiment(EXPERIMENT_NAME)

# ── Synthetic training data ────────────────────────────────────────────────
# Replace with real Delta Lake data: spark.table("swasthya.patients")

np.random.seed(42)
n = 2000

HIGH_RISK_OCCS = ["Miner", "Construction Worker", "Factory Worker", "Welder", "Farmer"]
LOW_RISK_OCCS  = ["Teacher", "Office Worker", "Healthcare Worker", "Shopkeeper"]

occupations = np.random.choice(HIGH_RISK_OCCS + LOW_RISK_OCCS, n)
ages        = np.random.randint(18, 70, n)
symptom_cnt = np.random.randint(0, 8, n)

# Risk label: higher if high-risk occupation + older + more symptoms
def label(occ, age, syms):
    score = 0
    if occ in HIGH_RISK_OCCS:
        score += 0.4
    if age > 50:
        score += 0.15
    score += syms * 0.06
    score += np.random.uniform(-0.1, 0.1)
    return int(score > 0.5)

labels = [label(o, a, s) for o, a, s in zip(occupations, ages, symptom_cnt)]

le = LabelEncoder()
occ_encoded = le.fit_transform(occupations)

df = pd.DataFrame({
    "occupation_encoded": occ_encoded,
    "age":                ages,
    "symptom_count":      symptom_cnt,
    "label":              labels,
})

# ── Train ──────────────────────────────────────────────────────────────────
X = df[["occupation_encoded", "age", "symptom_count"]]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run(run_name="rf_occupational_risk"):
    params = {"n_estimators": 200, "max_depth": 8, "class_weight": "balanced", "random_state": 42}
    mlflow.log_params(params)

    clf = RandomForestClassifier(**params)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, y_prob)
    mlflow.log_metric("auc_roc", auc)
    print(f"AUC-ROC: {auc:.4f}")
    print(classification_report(y_test, y_pred))

    # Log model
    signature = mlflow.models.infer_signature(X_train, clf.predict(X_train))
    mlflow.sklearn.log_model(
        clf,
        artifact_path="model",
        signature=signature,
        registered_model_name=MODEL_NAME,
    )

    print(f"✅ Model registered as: {MODEL_NAME}")
