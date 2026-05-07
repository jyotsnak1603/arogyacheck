"""
Risk analysis engine for ArogyaCheck.
Combines machine learning (Random Forest) for diabetes prediction with 
a heuristic weighted-score model for other cardiovascular risks.
"""
import joblib
import numpy as np
import os
import pandas as pd
from django.conf import settings

# Path to ML models
MODEL_PATH = os.path.join(settings.BASE_DIR, 'patients', 'ml', 'models', 'diabetes_model.joblib')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'patients', 'ml', 'models', 'scaler.joblib')
FEATURES_PATH = os.path.join(settings.BASE_DIR, 'patients', 'ml', 'models', 'features.joblib')

_model = None
_scaler = None
_features = None

def load_ml_components():
    """
    Loads the pre-trained ML model, scaler, and feature list from the filesystem.
    Uses global variables to cache components for better performance.
    """
    global _model, _scaler, _features
    if _model is None:
        try:
            _model = joblib.load(MODEL_PATH)
            _scaler = joblib.load(SCALER_PATH)
            _features = joblib.load(FEATURES_PATH)
        except Exception as e:
            print(f"Error loading ML models: {e}")
            return False
    return True

def calculate_risk(questionnaire, health_profile):
    """
    Main entry point for risk calculation.
    1. Uses ML for Diabetes prediction if components are available.
    2. Uses Heuristic weights for Hypertension and Heart Disease.
    3. Maps results to standardized risk levels (Low, Moderate, High).
    """
    from .models import RiskConfiguration
    
    # Try to use ML Model for Diabetes Risk
    ml_available = load_ml_components()
    ml_diabetes_prob = None
    
    if ml_available:
        # Prepare input for ML model
        # Features: ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        
        # Mapping logic
        pregnancies = 0 # Default
        glucose = 100 # Normal baseline
        if questionnaire.frequent_thirst or questionnaire.frequent_urination:
            glucose = 160 # Elevated
        if questionnaire.already_diabetic:
            glucose = 200 # High
            
        bp = 80 # Normal baseline
        if questionnaire.already_hypertensive:
            bp = 130 # High
            
        skin = 23 # Median
        insulin = 30 # Median
        bmi = health_profile.bmi()
        
        dpf = 0.47 # Median baseline
        if questionnaire.family_diabetes:
            dpf = 0.85 # High family history factor
            
        age = health_profile.age
        
        input_data = pd.DataFrame([[
            pregnancies, glucose, bp, skin, insulin, bmi, dpf, age
        ]], columns=_features)
        
        input_scaled = _scaler.transform(input_data)
        ml_diabetes_prob = _model.predict_proba(input_scaled)[0][1] # Probability of Outcome=1
        
    # Heuristic Fallback & Other Risks
    config = RiskConfiguration.objects.filter(is_active=True).first()
    if not config:
        config = RiskConfiguration()

    # Base score from heuristic for comparison or secondary risks
    base_score = 0
    if health_profile.bmi() >= 30: base_score += 15
    if health_profile.age >= 45: base_score += 10
    if questionnaire.smoking: base_score += 10
    if questionnaire.already_hypertensive: base_score += 15
    
    # Map ML probability to 0-100 score if available
    if ml_diabetes_prob is not None:
        overall_score = int(ml_diabetes_prob * 100)
    else:
        overall_score = min(base_score + 10, 100) # Fallback

    def get_level(s):
        if s < 30: return 'low'
        elif s < 60: return 'moderate'
        else: return 'high'

    # Risk classification
    diabetes_risk = get_level(overall_score)
    
    # Simple heuristic for others as we don't have separate ML models for them yet
    hypertension_score = base_score + (10 if questionnaire.already_hypertensive else 0)
    heart_score = base_score + (20 if questionnaire.chest_pain else 0)

    recommendation = get_recommendation(overall_score)

    return {
        'overall_score': overall_score,
        'diabetes_risk': diabetes_risk,
        'hypertension_risk': get_level(hypertension_score),
        'heart_risk': get_level(heart_score),
        'refer_for_test': overall_score >= 60,
        'recommendation': recommendation,
        'ml_probability': ml_diabetes_prob, # Additional metadata
    }

from django.utils.translation import gettext as _

def get_recommendation(score):
    """
    Returns localized actionable medical advice based on the overall risk score.
    """
    if score < 30:
        return _(
            "Your risk levels appear low. Maintain a healthy lifestyle "
            "with regular physical activity and a balanced diet. "
            "Continue annual health checkups as a precaution."
        )
    elif score < 60:
        return _(
            "You have a moderate risk level. We strongly recommend visiting "
            "your nearest Primary Health Centre for a basic checkup. "
            "Focus on improving physical activity, reducing smoking or alcohol "
            "if applicable, and maintaining a healthy diet."
        )
    else:
        return _(
            "Your risk level is high. Please visit a doctor immediately for "
            "lab tests including blood sugar, blood pressure, and lipid profile. "
            "Early detection can prevent serious complications. "
            "Do not ignore symptoms like chest pain or blurred vision."
        )
    