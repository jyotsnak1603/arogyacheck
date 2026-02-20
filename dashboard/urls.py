from django.urls import path
from . import views
urlpatterns = [
    path('asha/', views.asha_dashboard, name='asha_dashboard'),
    path('asha/register-patient/', views.register_patient, name='register_patient'),
    path('asha/patient/<int:patient_id>/', views.patient_detail_asha, name='patient_detail_asha'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/patient/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
]