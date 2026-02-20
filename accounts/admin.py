from django.contrib import admin

# Register your models here.
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role','phone', 'village', 'district','state','registered_by']
    list_filter = ['role', 'district', 'state']
    search_fields = ['user__username', 'user__first_name', 'phone','village']
    