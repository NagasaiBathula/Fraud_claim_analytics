// Power Query (M) Scripts for Data Ingestion
// In Power BI Desktop: Home -> Get Data -> Blank Query -> Advanced Editor
// Note: Update the file path in File.Contents() to match your local project directory if needed.

// QUERY 1: fraud_predictions
let
    Source = Csv.Document(File.Contents("outputs\fraud_predictions.csv"),[Delimiter=",", Columns=39, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"PolicyNumber", Int64.Type}, 
        {"FraudFound_P", Int64.Type}, 
        {"Actual_Fraud", Int64.Type}, 
        {"Predicted_Fraud", Int64.Type}, 
        {"Fraud_Probability", type number}, 
        {"Age", Int64.Type}, 
        {"Deductible", Int64.Type}, 
        {"DriverRating", Int64.Type}, 
        {"Year", Int64.Type}
    })
in
    #"Changed Type"


// QUERY 2: model_comparison
let
    Source = Csv.Document(File.Contents("outputs\model_comparison.csv"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Model", type text}, 
        {"Accuracy", type number}, 
        {"Precision", type number}, 
        {"Recall", type number}, 
        {"F1_Score", type number}, 
        {"ROC_AUC", type number}, 
        {"True_Negatives", Int64.Type}, 
        {"False_Positives", Int64.Type}, 
        {"False_Negatives", Int64.Type}, 
        {"True_Positives", Int64.Type}
    })
in
    #"Changed Type"
