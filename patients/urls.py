from django.urls import path
from . import views
urlpatterns = [
    path('questionnaire/', views.questionnaire_view, name='questionnaire'),
    path('report/', views.report_view, name = 'report'),
]