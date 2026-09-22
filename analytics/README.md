# Module 2 — Analytics Pipeline

## Overview

This module implements an end-to-end Titanic analytics and machine-learning
workflow.

The pipeline consists of:

1. Dataset profiling
2. Missing-value analysis and cleaning
3. Univariate analysis
4. Bivariate analysis
5. Multivariate data story
6. Standardization sanity check
7. Stratified train/test split
8. Leakage-safe preprocessing
9. Logistic Regression
10. Decision Tree
11. Random Forest
12. Class imbalance comparison
13. Random Forest hyperparameter tuning
14. Linear regression for fare prediction
15. Model comparison
16. Complete pipeline persistence

## Files

### 01_eda.ipynb

Performs:

- Titanic dataset loading
- Dataset profiling
- Missing-value analysis
- Cleaning
- Univariate analysis
- Bivariate analysis
- Correlation analysis
- Multivariate visualizations
- Standardization check
- Saves `titanic.csv`

### 02_modeling.ipynb

Performs:

- Stratified train/test split
- Leakage-safe preprocessing
- Classification
- Classification evaluation
- Imbalance comparison
- SMOTE
- Random Forest GridSearchCV
- OOB evaluation
- Regression
- Regression evaluation
- Residual analysis
- Complete model pipeline persistence

## Dataset

The Titanic dataset is loaded once using:

`sns.load_dataset("titanic")`

The resulting cleaned dataset is committed as:

`analytics/titanic.csv`

The modeling notebook reads the committed CSV rather than loading the
dataset independently.

## Preprocessing

Classification preprocessing includes:

- Median imputation for numeric features
- Most-frequent imputation for categorical features
- One-hot encoding
- StandardScaler

All preprocessing is implemented inside a scikit-learn Pipeline and is
fitted only on training data.

## Model Artifact

The final fitted pipeline is saved as:

`models/best_pipeline.joblib`

The saved artifact contains both preprocessing and the final estimator,
allowing raw input data to be passed directly to the model.

## Outputs

Generated visualizations are stored inside:

`analytics/outputs/`
`analytics/models/`
