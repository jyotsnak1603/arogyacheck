"""
Machine Learning training pipeline for ArogyaCheck.
Trains a Random Forest classifier on the Pima Indians Diabetes dataset.
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import os

# 1. Collect Dataset (Pima Indians Diabetes Dataset)
DATA_URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
COLUMNS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome'
]

def train_health_model():
    """
    Orchestrates the ML lifecycle:
    1. Data Collection: Downloads Pima Indians dataset.
    2. Cleaning: Handles missing values and outliers.
    3. Preprocessing: Scaling and train/test splits.
    4. Model Selection: Compares Logistic Regression and Random Forest.
    5. Hyperparameter Tuning: Optimized RF using GridSearchCV.
    6. Serialization: Saves model, scaler, and features for production use.
    """
    print("Downloading dataset...")
    df = pd.read_csv(DATA_URL, names=COLUMNS)

    # 2. Clean Data
    print("Cleaning data...")
    # Handle zeros in columns where zero is not physically possible (Missing values)
    cols_with_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in cols_with_zeros:
        df[col] = df[col].replace(0, np.nan)
        # Fill missing values with median
        df[col] = df[col].fillna(df[col].median())

    # Remove outliers using IQR
    for col in COLUMNS[:-1]:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    # 3. Preprocessing
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    # Split data (80/20) with stratification for class imbalance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Train Models with Class Weighting
    print(f"Dataset Size: {len(df)} samples")
    print(f"Features: {list(X.columns)}")
    print(f"Class Distribution: {y.value_counts(normalize=True).to_dict()}")

    models = {
        'Logistic Regression': LogisticRegression(class_weight='balanced', max_iter=1000),
        'Random Forest': RandomForestClassifier(class_weight='balanced', random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        
        # Overfitting check
        train_acc = model.score(X_train_scaled, y_train)
        test_acc = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        
        results[name] = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred),
            'Recall': recall_score(y_test, y_pred),
            'F1': f1_score(y_test, y_pred),
            'Train Acc': train_acc,
            'Test Acc': test_acc
        }
        print(f"\n{name} Results:")
        print(f"Train Accuracy: {train_acc:.4f}, Test Accuracy: {test_acc:.4f}")
        print(classification_report(y_test, y_pred))

    # 5. Hyperparameter Tuning (with Stratified CV)
    print("Tuning Random Forest with Stratified CV...")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 15],
        'min_samples_split': [2, 5]
    }
    from sklearn.model_selection import StratifiedKFold
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        RandomForestClassifier(class_weight='balanced', random_state=42), 
        param_grid, cv=cv, scoring='f1'
    )
    grid_search.fit(X_train_scaled, y_train)

    best_rf = grid_search.best_estimator_
    print(f"Best RF Params: {grid_search.best_params_}")

    # 6. Serialization
    print("Saving model and scaler...")
    os.makedirs('patients/ml/models', exist_ok=True)
    joblib.dump(best_rf, 'patients/ml/models/diabetes_model.joblib')
    joblib.dump(scaler, 'patients/ml/models/scaler.joblib')
    joblib.dump(COLUMNS[:-1], 'patients/ml/models/features.joblib')
    
    print("Training complete!")

if __name__ == "__main__":
    train_health_model()
