from django.contrib import admin

# Register your models here.
from .models import HealthProfile, Questionnaire, RiskReport

@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    
    list_display = ['patient', 'age', 'gender', 'weight_kg', 'height_cm']
    search_fields = ['patient__username', 'patient__first_name']
    list_filter = ['gender']

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):

    list_display = ['health_profile', 'submitted_at', 'physical_activity', 'smoking', 'alcohol']
    list_filter = ['physical_activity', 'smoking', 'alcohol']
    date_hierarchy = 'submitted_at'

@admin.register(RiskReport)
class RiskReportAdmin(admin.ModelAdmin):

    list_display = ['questionnaire', 'overall_score', 'diabetes_risk',
                    'hypertension_risk', 'heart_risk', 'refer_for_test', 'reviewed_by_doctor']
    
    list_filter = ['diabetes_risk', 'hypertension_risk', 'heart_risk',
                   'refer_for_test', 'reviewed_by_doctor']
    
    readonly_fields = ['overall_score', 'diabetes_risk', 'hypertension_risk',
                       'heart_risk', 'refer_for_test', 'recommendation']