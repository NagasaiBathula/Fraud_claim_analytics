"""
Vehicle Insurance Claim Fraud Detection
Machine Learning Pipeline

This script performs:
1. Data loading and validation of the Oracle insurance claims dataset.
2. Anomaly handling (imputing zero-day claim dates and zero-age driver entries).
3. Feature engineering and data preprocessing (StandardScaler + OneHotEncoder).
4. Training and evaluation of multiple classification models with class balancing.
5. Exporting model comparison metrics and full predictions for the Power BI dashboard.
"""

import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.utils.class_weight import compute_sample_weight


def load_dataset(file_path="dataset/fraud_oracle.csv"):
    """Loads the raw vehicle insurance claims dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found at '{file_path}'. Please verify the path."
        )

    df = pd.read_csv(file_path)
    print(f"Loaded dataset: {df.shape[0]:,} records, {df.shape[1]} features")
    return df


def clean_and_prepare_data(df):
    """
    Cleans known anomalies in the dataset:
    - Fixes records where DayOfWeekClaimed / MonthClaimed was recorded as '0'
      by using the incident accident date.
    - Imputes Age == 0 entries to 16 (corresponding to young drivers).
    - Adds readable category labels and age group bins for dashboard filtering.
    """
    data = df.copy()

    # Address claim date anomalies
    zero_claimed = (data["DayOfWeekClaimed"] == "0") | (data["MonthClaimed"] == "0")
    if zero_claimed.sum() > 0:
        data.loc[zero_claimed, "DayOfWeekClaimed"] = data.loc[zero_claimed, "DayOfWeek"]
        data.loc[zero_claimed, "MonthClaimed"] = data.loc[zero_claimed, "Month"]
        print(f"Fixed {zero_claimed.sum()} record(s) with '0' claim date.")

    # Fix driver age anomaly
    zero_age = data["Age"] == 0
    if zero_age.sum() > 0:
        data.loc[zero_age, "Age"] = 16
        print(f"Imputed {zero_age.sum()} record(s) where Age was 0 to 16.")

    # Categorical bins for reporting
    data["Actual_Fraud_Status"] = data["FraudFound_P"].map(
        {0: "Genuine", 1: "Fraudulent"}
    )
    bins = [0, 25, 35, 50, 65, 120]
    labels = ["16-25", "26-35", "36-50", "51-65", "Over 65"]
    data["Age_Group"] = pd.cut(data["Age"], bins=bins, labels=labels, right=True)

    return data


def build_preprocessor(cat_cols, num_cols):
    """Creates a ColumnTransformer pipeline for scaling and one-hot encoding."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            (
                "cat",
                OneHotEncoder(
                    drop="first", sparse_output=False, handle_unknown="ignore"
                ),
                cat_cols,
            ),
        ]
    )


def initialize_models():
    """Initializes candidate models configured to handle high class imbalance."""
    return {
        "Logistic Regression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            class_weight="balanced", max_depth=5, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            class_weight="balanced",
            n_estimators=100,
            max_depth=8,
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
        ),
    }


def train_and_evaluate_models(models, X_train_proc, y_train, X_test_proc, y_test):
    """Fits each candidate model, evaluates performance metrics on the test split."""
    sample_weights_train = compute_sample_weight("balanced", y_train)
    results = []
    fitted_models = {}

    print("\nTraining and evaluating models:")
    print("-" * 75)
    print(
        f"{'Model':<22} | {'Accuracy':<9} | {'Precision':<9} | {'Recall':<9} | {'F1':<7} | {'ROC-AUC':<7}"
    )
    print("-" * 75)

    for name, model in models.items():
        if name == "Gradient Boosting":
            model.fit(X_train_proc, y_train, sample_weight=sample_weights_train)
        else:
            model.fit(X_train_proc, y_train)

        y_pred = model.predict(X_test_proc)
        y_prob = model.predict_proba(X_test_proc)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        fitted_models[name] = model
        results.append(
            {
                "Model": name,
                "Accuracy": round(acc, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1_Score": round(f1, 4),
                "ROC_AUC": round(auc, 4),
            }
        )

        print(
            f"{name:<22} | {acc * 100:>8.2f}% | {prec * 100:>8.2f}% | {rec * 100:>8.2f}% | {f1:>7.4f} | {auc:>7.4f}"
        )

    print("-" * 75)
    comparison_df = pd.DataFrame(results)
    best_name = (
        comparison_df.sort_values(by=["ROC_AUC", "F1_Score"], ascending=False)
        .iloc[0]["Model"]
    )
    print(f"Selected best performing model: {best_name}")

    return fitted_models, comparison_df, best_name


def export_predictions_and_metrics(
    df, feature_cols, preprocessor, best_model, comparison_df, output_dir="outputs"
):
    """
    Computes probabilities and risk tiers for all records and saves
    the resulting CSVs used by Power BI.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save model comparison table
    comparison_path = os.path.join(output_dir, "model_comparison.csv")
    comparison_df.to_csv(comparison_path, index=False)
    print(f"Saved model metrics to '{comparison_path}'")

    # Score full dataset with best model
    X_all_proc = preprocessor.transform(df[feature_cols])
    preds = best_model.predict(X_all_proc)
    probs = best_model.predict_proba(X_all_proc)[:, 1]

    # Assign risk tier based on fraud probability thresholds
    risk_tiers = np.where(
        probs < 0.35, "Low Risk", np.where(probs < 0.65, "Medium Risk", "High Risk")
    )

    scored_df = df.copy()
    scored_df["Actual_Fraud"] = df["FraudFound_P"]
    scored_df["Predicted_Fraud"] = preds
    scored_df["Predicted_Fraud_Status"] = np.where(
        preds == 1, "Predicted Fraudulent", "Predicted Genuine"
    )
    scored_df["Fraud_Probability"] = np.round(probs, 4)
    scored_df["Risk_Category"] = risk_tiers

    predictions_path = os.path.join(output_dir, "fraud_predictions.csv")
    scored_df.to_csv(predictions_path, index=False)
    print(f"Saved full predictions to '{predictions_path}' ({scored_df.shape[0]:,} rows)")


def main():
    print("Starting Insurance Fraud Detection ML Pipeline...")

    # 1. Load data
    df = load_dataset("dataset/fraud_oracle.csv")

    # 2. Clean data
    df_clean = clean_and_prepare_data(df)

    # 3. Prepare features
    target = "FraudFound_P"
    excluded_cols = ["PolicyNumber", "FraudFound_P", "Actual_Fraud_Status", "Age_Group"]
    feature_cols = [col for col in df_clean.columns if col not in excluded_cols]

    cat_cols = df_clean[feature_cols].select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = df_clean[feature_cols].select_dtypes(include=["int64", "float64"]).columns.tolist()

    X = df_clean[feature_cols]
    y = df_clean[target]

    # Stratified train-test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # 4. Preprocess features
    preprocessor = build_preprocessor(cat_cols, num_cols)
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    # 5. Model training & evaluation
    models = initialize_models()
    fitted_models, comparison_df, best_name = train_and_evaluate_models(
        models, X_train_proc, y_train, X_test_proc, y_test
    )

    # 6. Export outputs for Power BI
    export_predictions_and_metrics(
        df_clean,
        feature_cols,
        preprocessor,
        fitted_models[best_name],
        comparison_df,
    )
    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
