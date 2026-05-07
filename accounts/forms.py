from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

#Below 2 importing modules for Password Complexity

from django.contrib.auth.password_validation import validate_password    
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    #USer fields
    first_name = forms.CharField(max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    last_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    username = forms.CharField(max_length=50, 
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    #UserProfile fields
    role = forms.ChoiceField(choices=UserProfile.ROLES,
                              widget=forms.Select(attrs={'class': 'form-select'}))
    
    phone = forms.CharField(max_length=10,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    village = forms.CharField(max_length=100,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    district = forms.CharField(max_length=100,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=100,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', list(e.messages))

        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Emailis already registered. Try logging in or register using different account")
        return email
    