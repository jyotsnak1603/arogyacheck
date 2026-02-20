from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #Create user
            user = User.objects.create_user(
                username= form.cleaned_data['username'],
                email= form.cleaned_data['email'],
                password= form.cleaned_data['password'],
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
            )

            #Creating USerProfile

            UserProfile.objects.create(
                user=user,
                role = form.cleaned_data['role'],
                phone = form.cleaned_data['phone'],
                village = form.cleaned_data['village'],
                district = form.cleaned_data['district'],
                state = form.cleaned_data['state'],
            )

            messages.success(request, "Account Created Successfully! Please login.")
            return redirect('login')
        
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
        
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password = password)
        if user is not None:
            login(request, user)
        #Redirect according to their roles
            role = user.userprofile.role
            if role == 'patient':
                return redirect('questionnaire')
            elif role == 'asha':
                return redirect('asha_dashboard')
            elif role == 'doctor':
                return redirect('doctor_dashboard')
            
        else:
            messages.error(request, "Invalid username or password.Try again!")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')