from django import forms
from .models import HealthProfile, Questionnaire

class HealthProfileForm(forms.ModelForm):
    class Meta:
        model = HealthProfile
        fields = ['age', 'gender', 'weight_kg', 'height_cm']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        exclude = ['health_profile', 'submitted_at']
        widgets = {
            # Lifestyle
            'physical_activity': forms.Select(attrs={'class': 'form-select'}),
            'diet_type': forms.Select(attrs={'class': 'form-select'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-control'}),

            # Symptoms
            'smoking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alcohol': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequent_thirst': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequent_urination': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fatigue': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'blurred_vision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chest_pain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shortness_of_breath': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numbness_in_feet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Family History
            'family_diabetes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'family_hypertension': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'family_heart_disease': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'family_kidney_disease': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Existing Conditions
            'already_diabetic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'already_hypertensive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }