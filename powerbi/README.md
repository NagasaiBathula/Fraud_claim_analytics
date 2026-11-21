# Power BI Dashboard Architecture & Build Guide
## Project: Insurance Claim Fraud Detection Using Machine Learning and Power BI

### 1. Data Connection in Power BI Desktop
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Select `outputs/fraud_predictions.csv` and click **Load**.
4. Click **Get Data** -> **Text/CSV** again and select `outputs/model_comparison.csv` and click **Load**.
5. Switch to the **Model View** and verify the tables.

---

### 2. Adding DAX Measures
Create a dedicated measures table or add the formulas from `powerbi/DAX_Measures.dax`:
- Right-click `fraud_predictions` -> **New Measure**.
- Paste each DAX formula (e.g. `Total Claims`, `Actual Fraudulent Claims`, `Actual Fraud Rate %`, `Model Precision %`, `Model Recall %`).

---

### 3. Report Layout & Visual Design (3 Pages)

#### PAGE 1: OVERVIEW (Executive Fraud Summary)
- **Header Banner:** Title "Insurance Claim Fraud Detection - Executive Overview" with corporate navy theme (`#1a365d`).
- **KPI Card Row:**
  1. `Total Claims`: 15,420
  2. `Actual Fraudulent Claims`: 923
  3. `Fraud Rate %`: 5.99%
  4. `Predicted Fraudulent Claims`: 4,891
  5. `High Risk Claims`: 1,460
- **Visual 1 (Donut Chart):** Actual Fraud Status (`FraudFound_P` mapped to Genuine vs Fraudulent). Colors: Navy Blue (`#2b6cb0`) and Crimson Red (`#e53e3e`).
- **Visual 2 (Clustered Column Chart):** Claims by `VehicleCategory` (Sedan, Sport, Utility) grouped by `Actual_Fraud_Status`.
- **Visual 3 (Stacked Bar Chart):** Claims by `AccidentArea` (Urban vs Rural) broken down by Fraud Status.
- **Visual 4 (Card / Gauge):** Average Predicted Fraud Probability.

#### PAGE 2: FRAUD ANALYSIS (Risk Factors & Driver Demographics)
- **Top Slicers Panel:**
  - `AccidentArea` (Urban / Rural)
  - `Year` (1994 / 1995 / 1996)
  - `VehicleCategory` (Sedan / Sport / Utility)
  - `Risk_Category` (Low Risk / Medium Risk / High Risk)
- **Visual 1 (Clustered Column Chart):** Fraud Rate % by `Age_Group` (`16-25`, `26-35`, `36-50`, `51-65`, `Over 65`).
- **Visual 2 (Horizontal Bar Chart):** Claims & Fraud Rate by `AgeOfVehicle` (new, 2 years, 3 years, etc.).
- **Visual 3 (Treemap / Bar Chart):** Fraud Rate by `PolicyType` (e.g., Sedan - Collision, Sedan - All Perils).
- **Visual 4 (Line / Clustered Bar):** Fraud Counts by `PastNumberOfClaims` ('none', '1', '2 to 4', 'more than 4').
- **Visual 5 (Summary Table):** High-risk vehicle makes and driver ratings.

#### PAGE 3: MODEL PERFORMANCE (Machine Learning Evaluation)
- **Header:** "Machine Learning Algorithm Comparison & Validation"
- **Visual 1 (Table / Matrix):**
  - Source: `model_comparison`
  - Columns: `Model`, `Accuracy`, `Precision`, `Recall`, `F1_Score`, `ROC_AUC`.
- **Visual 2 (Clustered Bar Chart):**
  - Comparing the 4 algorithms across `Recall %`, `ROC_AUC`, and `F1_Score`.
- **Visual 3 (Confusion Matrix Table):**
  - Matrix visual using `Actual_Fraud_Status` as rows and `Predicted_Fraud_Status` as columns, with Values = `Total Claims`.
  - Clearly shows True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN).
- **Visual 4 (Histogram / Density Column):**
  - Distribution of `Fraud_Probability` grouped into risk bands.
- **Callout Box / Key Takeaway:**
  - Explains why **Gradient Boosting** is the best model: it achieves an **ROC-AUC of 0.8419** and a **Recall of 88.11%**, capturing the vast majority of fraudulent claims while significantly reducing financial exposure.

---

### 4. Viva Presentation Key Questions & Answers
- **Q: Why is Recall more important than Accuracy in fraud detection?**
  *A: Because genuine claims make up 94% of the dataset. A dumb model predicting 0 for all claims would get 94% accuracy but 0% recall, catching zero frauds. High recall ensures that fraudulent claims are caught.*
- **Q: How does the model connect to Power BI?**
  *A: The trained Scikit-learn model generates prediction probabilities and risk tiers saved directly into `fraud_predictions.csv`, which Power BI ingests to drive interactive visuals and KPI filtering.*
