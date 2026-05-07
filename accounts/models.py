from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLES = [
        ('patient', 'Patient'),
        ('asha', 'ASHA Worker'),
        ('doctor','Doctor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    phone = models.CharField(max_length=10)
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    registered_by = models.ForeignKey(User,
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      blank=True,
                                      related_name='registered_patients'
                                      )
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    