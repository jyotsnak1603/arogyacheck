from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import UserProfile

#To reset password
from django.core.mail import send_mail
from django.conf import settings
import uuid

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            role = form.cleaned_data['role']

            # Generate token for doctor
            token = str(uuid.uuid4()) if role == 'doctor' else ''

            UserProfile.objects.create(
                user=user,
                role=role,
                phone=form.cleaned_data['phone'],
                village=form.cleaned_data['village'],
                district=form.cleaned_data['district'],
                state=form.cleaned_data['state'],
                is_verified=False if role == 'doctor' else True,
                verification_token=token,
            )

            # Assign user to group based on role
            from django.contrib.auth.models import Group
            group_name_map = {
                'patient': 'Patient',
                'asha': 'ASHA Worker',
                'doctor': 'Doctor',
            }
            group_name = group_name_map.get(role)
            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass

            # Send verification email for doctor
            if role == 'doctor':
                verify_link = f"http://127.0.0.1:8000/accounts/verify-email/{token}/"
                send_mail(
                    'ArogyaCheck - Verify Your Doctor Account',
                    f'Hello Dr. {user.first_name},\n\nClick this link to verify your account:\n{verify_link}\n\nIf you did not register, ignore this email.',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, "Account created! Please check your email to verify your doctor account.")
            else:
                messages.success(request, "Account created successfully! Please login.")

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
            # Block unverified doctors
            if user.userprofile.role == 'doctor' and not user.userprofile.is_verified:
                messages.error(request, "Please verify your email before logging in as a doctor.")
                return render(request, 'accounts/login.html')
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

# Temporary in-memory token store
reset_tokens = {}

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = str(uuid.uuid4())
            reset_tokens[token] = user.id
            reset_link = f"http://127.0.0.1:8000/accounts/password-reset-confirm/{token}/"
            send_mail(
                'ArogyaCheck Password Reset',
                f'Click this link to reset your password: {reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, "Password reset link sent to your email!")
            return redirect('login')
        else:
            messages.error(request, "No account found with this email.")
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm_view(request, token):
    if token not in reset_tokens:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user = User.objects.get(id=reset_tokens[token])
            user.set_password(password)
            user.save()
            del reset_tokens[token]
            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')

    return render(request, 'accounts/password_reset_confirm.html', {'token': token})


def verify_email_view(request, token):
    try:
        profile = UserProfile.objects.get(verification_token=token, role='doctor')
        profile.is_verified = True
        profile.verification_token = ''
        profile.save()
        messages.success(request, "Email verified successfully! You can now login.")
    except UserProfile.DoesNotExist:
        messages.error(request, "Invalid or expired verification link.")
    return redirect('login')