from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.
from .models import UserProfile

#UserProfile inside UserAdmin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['role', 'phone', 'village', 'district', 'state', 'is_verified']

# Custom User Admin with Profile inline
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role','phone', 'village', 'district','state','registered_by']
    list_filter = ['role', 'district', 'state']
    search_fields = ['user__username', 'user__first_name', 'phone','village']
    