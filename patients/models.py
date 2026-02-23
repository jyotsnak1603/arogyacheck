from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class HealthProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    patient = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    weight_kg = models.FloatField()
    height_cm = models.FloatField()

    def bmi(self):
        return round(self.weight_kg / ((self.height_cm / 100) ** 2), 2)
    
    def __str__(self):
        return f"{self.patient.username} - Age {self.age}"
    
class Questionnaire(models.Model):
    ACTIVITY_CHOICES = [
        ('none', 'No Physical Activity'),
        ('light', 'Light(Walking occasionally)'),
        ('moderate', 'Moderate (Exercise 3x/week)'),
        ('heavy', 'Heavy (Daily intense exercise)'),
    ]
    DIET_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non_veg', 'Non Vegetarian'),
        ('mixed', 'Mixed'),
    ]

    health_profile = models.ForeignKey(
        HealthProfile,
        on_delete=models.CASCADE,
        related_name='questionnaires'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    #Lifestyle
    physical_activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES)
    smoking = models.BooleanField(default=False)
    alcohol = models.BooleanField(default=False)
    sleep_hours = models.IntegerField()

    #Symptoms
    frequent_thirst = models.BooleanField(default=False)
    frequent_urination = models.BooleanField(default=False)
    fatigue = models.BooleanField(default=False)
    blurred_vision = models.BooleanField(default=False)
    chest_pain = models.BooleanField(default=False)
    shortness_of_breath = models.BooleanField(default=False)
    numbness_in_feet = models.BooleanField(default=False)

    #Family History
    family_diabetes = models.BooleanField(default=False)
    family_hypertension = models.BooleanField(default=False)
    family_heart_disease = models.BooleanField(default=False)
    family_kidney_disease = models.BooleanField(default=False)

    #Existing Conditions
    already_diabetic = models.BooleanField(default=False)
    already_hypertensive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.health_profile.patient.username} - {self.submitted_at.date()}"

class RiskReport(models.Model):
    RISK_LEVELS = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.CASCADE,
        related_name='report'
    )

    generated_at = models.DateTimeField(auto_now_add=True)
    overall_score = models.IntegerField()
    diabetes_risk = models.CharField(max_length=10, choices=RISK_LEVELS)
    hypertension_risk = models.CharField(max_length=10, choices=RISK_LEVELS)
    heart_risk = models.CharField(max_length=10, choices=RISK_LEVELS)
    refer_for_test = models.BooleanField(default=False)
    recommendation = models.TextField()
    reviewed_by_doctor = models.BooleanField(default=False)
    doctor_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.questionnaire.health_profile.patient.username} - Score {self.overall_score}"
    

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('register_patient', 'Registered Patient'),
        ('submit_questionnaire', 'Submitted Questionnaire'),
        ('mark_reviewed', 'Marked as Reviewed'),
    ]
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='audit_logs')
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.performed_by} - {self.action} - {self.timestamp}"