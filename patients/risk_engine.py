def calculate_risk(questionnaire, health_profile):
    from .models import RiskConfiguration
    
    # Get active config or use defaults
    config = RiskConfiguration.objects.filter(is_active=True).first()
    if not config:
        # Fallback to an object with default values if DB is empty
        config = RiskConfiguration()

    score = 0

    # BMI Factor
    bmi = health_profile.bmi()
    if bmi >= 35:
        score += config.bmi_obese_weight
    elif bmi >= 30:
        score += config.bmi_overweight_high
    elif bmi >= 25:
        score += config.bmi_overweight_low

    # Age Factor
    age = health_profile.age
    if age >= 60:
        score += config.age_elderly_weight
    elif age >= 45:
        score += config.age_senior_weight
    elif age >= 35:
        score += config.age_middle_weight
    
    # Lifestyle Factors
    if questionnaire.smoking:
        score += config.smoking_weight
    if questionnaire.alcohol:
        score += config.alcohol_weight
    
    if questionnaire.physical_activity == 'none':
        score += config.inactivity_weight
    elif questionnaire.physical_activity == 'light':
        score += config.light_activity_weight
        
    if questionnaire.sleep_hours < 6:
        score += config.sleep_deprivation_weight
    
    # Symptoms
    symptom_fields = [
        'frequent_thirst', 'frequent_urination', 'fatigue',
        'blurred_vision', 'chest_pain', 'shortness_of_breath',
        'numbness_in_feet',
    ]
    for field in symptom_fields:
        if getattr(questionnaire, field):
            score += config.symptom_weight
        
    # Family History
    family_fields = [
        'family_diabetes', 'family_hypertension',
        'family_heart_disease', 'family_kidney_disease'
    ]
    for field in family_fields:
        if getattr(questionnaire, field):
            score += config.family_history_weight

    # Existing Conditions
    if questionnaire.already_diabetic:
        score += config.diabetes_existing_weight
    if questionnaire.already_hypertensive:
        score += config.hypertension_existing_weight

    # Cap score at 100
    score = min(score, 100)

    # Derive Risk levels
    def get_level(s):
        if s < 30:
            return 'low'
        elif s < 60:
            return 'moderate'
        else:
            return 'high'

    # Disease specific scores (using base score as baseline)
    diabetes_score = score
    if questionnaire.frequent_thirst: diabetes_score += 5
    if questionnaire.frequent_urination: diabetes_score += 5
    if questionnaire.family_diabetes: diabetes_score += 5
    diabetes_score = min(diabetes_score, 100)

    hypertension_score = score
    if questionnaire.chest_pain: hypertension_score += 5
    if questionnaire.shortness_of_breath: hypertension_score += 5
    if questionnaire.family_hypertension: hypertension_score += 5
    hypertension_score = min(hypertension_score, 100)

    heart_score = score
    if questionnaire.chest_pain: heart_score += 8
    if questionnaire.shortness_of_breath: heart_score += 8
    if questionnaire.family_heart_disease: heart_score += 8
    heart_score = min(heart_score, 100)

    recommendation = get_recommendation(score)

    return {
        'overall_score': score,
        'diabetes_risk': get_level(diabetes_score),
        'hypertension_risk': get_level(hypertension_score),
        'heart_risk': get_level(heart_score),
        'refer_for_test': score >= 60,
        'recommendation': recommendation,
    }


from django.utils.translation import gettext as _

def get_recommendation(score):
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
    