from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
]