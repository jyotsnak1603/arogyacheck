def calculate_risk(questionnaire, health_profile):
    score = 0

    # BMI Factor (max 20 points)
    bmi = health_profile.bmi()
    if bmi>=35:
        score+=20
    elif bmi >=30:
        score+=15
    elif bmi >=25:
        score+=10

    #Age Factor (max 15 points)
    age = health_profile.age
    if age >= 60:
        score += 15
    elif age >= 45:
        score += 10
    elif age >= 35:
        score += 5
    
    #Lifestyle Factors (max 25 points)
    if questionnaire.smoking:
        score += 10
    if questionnaire.alcohol:
        score += 5
    if questionnaire.physical_activity == 'none':
        score += 10
    elif questionnaire.physical_activity == 'light':
        score += 5
    if questionnaire.sleep_hours < 6:
        score += 5
    elif questionnaire.sleep_hours > 9:
        score += 3
    
    #Symptoms (max 35 points)
    symptom_fields = [
        'frequent_thirst',
        'frequent_urination',
        'fatigue',
        'blurred_vision',
        'chest_pain',
        'shortness_of_breath',
        'numbness_in_feet',
    ]
    for field in symptom_fields:
        if getattr(questionnaire, field):
            score += 5
        
    #Family History (max 20 points)
    if questionnaire.family_diabetes:
        score += 5
    if questionnaire.family_hypertension:
        score += 5
    if questionnaire.family_heart_disease:
        score += 5
    if questionnaire.family_kidney_disease:
        score += 5

    #EXisting Condtion (max 20 points)
    if questionnaire.already_diabetic:
        score += 10
    if questionnaire.already_hypertensive:
        score += 10

    #Cap score at 100
    score = min(score, 100)

    #Derive Risk levels
    def get_level(s):
        if s < 30:
            return 'low'
        elif s < 60:
            return 'moderate'
        else:
            return 'high'
    overall_level = get_level(score)

    #Disease specofic scores
    #Diabetes score
    diabetes_score = score
    if questionnaire.frequent_thirst:
        diabetes_score += 5
    if questionnaire.frequent_urination:
        diabetes_score += 5
    if questionnaire.family_diabetes:
        diabetes_score += 5
    diabetes_score = min(diabetes_score, 100)

    # Hypertension leaning score
    hypertension_score = score
    if questionnaire.chest_pain:
        hypertension_score += 5
    if questionnaire.shortness_of_breath:
        hypertension_score += 5
    if questionnaire.family_hypertension:
        hypertension_score += 5
    hypertension_score = min(hypertension_score, 100)

    # Heart disease leaning score
    heart_score = score
    if questionnaire.chest_pain:
        heart_score += 8
    if questionnaire.shortness_of_breath:
        heart_score += 8
    if questionnaire.family_heart_disease:
        heart_score += 8
    heart_score = min(heart_score, 100)

    # ─── Recommendation Text ──────────────────────────────
    recommendation = get_recommendation(score)

    return {
        'overall_score': score,
        'diabetes_risk': get_level(diabetes_score),
        'hypertension_risk': get_level(hypertension_score),
        'heart_risk': get_level(heart_score),
        'refer_for_test': score >= 60,
        'recommendation': recommendation,
    }


def get_recommendation(score):
    if score < 30:
        return (
            "Your risk levels appear low. Maintain a healthy lifestyle "
            "with regular physical activity and a balanced diet. "
            "Continue annual health checkups as a precaution."
        )
    elif score < 60:
        return (
            "You have a moderate risk level. We strongly recommend visiting "
            "your nearest Primary Health Centre for a basic checkup. "
            "Focus on improving physical activity, reducing smoking or alcohol "
            "if applicable, and maintaining a healthy diet."
        )
    else:
        return (
            "Your risk level is high. Please visit a doctor immediately for "
            "lab tests including blood sugar, blood pressure, and lipid profile. "
            "Early detection can prevent serious complications. "
            "Do not ignore symptoms like chest pain or blurred vision."
        )
    