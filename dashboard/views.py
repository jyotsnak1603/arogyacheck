from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import UserProfile
from accounts.forms import RegisterForm
from patients.models import HealthProfile, Questionnaire, RiskReport, AuditLog
from patients.forms import HealthProfileForm, QuestionnaireForm
from patients.risk_engine import calculate_risk


def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                if request.user.userprofile.role != role:
                    messages.error(request, "You are not authorized to view this page.")
                    return redirect('login')
            except UserProfile.DoesNotExist:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
@role_required('asha')
def asha_dashboard(request):

    #Get all patients registered by specific ASHA worker
    registered_profiles = UserProfile.objects.filter(
        registered_by=request.user,
        role='patient').select_related('user')
    
    #Geting latest risk report for each patient
    patients_data = []
    for profile in registered_profiles:
        try:
            health_profile = HealthProfile.objects.get(patient=profile.user)
            latest_q = health_profile.questionnaires.latest('submitted_at')
            report = latest_q.report
        except (HealthProfile.DoesNotExist, Questionnaire.DoesNotExist,
                RiskReport.DoesNotExist):
            report = None
        patients_data.append({
            'profile': profile,
            'report': report,
        })

    return render(request, 'dashboard/asha_dashboard.html', 
                  {'patients_data': patients_data})

@login_required
@role_required('asha')
def register_patient(request):
    if request.method == 'POST':
        # Force role to patient
        post_data = request.POST.copy()
        post_data['role'] = 'patient'

        user_form = RegisterForm(post_data)
        profile_form = HealthProfileForm(post_data)
        questionnaire_form = QuestionnaireForm(post_data)

        # Debug — check terminal
        print("User form errors:", user_form.errors)
        print("Profile form errors:", profile_form.errors)
        print("Questionnaire form errors:", questionnaire_form.errors)

        if user_form.is_valid() and profile_form.is_valid() and questionnaire_form.is_valid():
            user = User.objects.create_user(
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data['email'],
                password=user_form.cleaned_data['password'],
                first_name=user_form.cleaned_data['first_name'],
                last_name=user_form.cleaned_data['last_name'],
            )
            UserProfile.objects.create(
                user=user,
                role='patient',
                phone=user_form.cleaned_data['phone'],
                village=user_form.cleaned_data['village'],
                district=user_form.cleaned_data['district'],
                state=user_form.cleaned_data['state'],
                registered_by=request.user,
            )
            health_profile = profile_form.save(commit=False)
            health_profile.patient = user
            health_profile.save()

            questionnaire = questionnaire_form.save(commit=False)
            questionnaire.health_profile = health_profile
            questionnaire.save()

            result = calculate_risk(questionnaire, health_profile)
            RiskReport.objects.create(
                questionnaire=questionnaire,
                overall_score=result['overall_score'],
                diabetes_risk=result['diabetes_risk'],
                hypertension_risk=result['hypertension_risk'],
                heart_risk=result['heart_risk'],
                refer_for_test=result['refer_for_test'],
                recommendation=result['recommendation'],
            )
            AuditLog.objects.create(
                action='register_patient',
                performed_by=request.user,
                patient=user,
                details=f"Patient {user.get_full_name()} registered from {user.userprofile.village}") 
            
            messages.success(request, f"Patient {user.first_name} registered successfully!")
            return redirect('asha_dashboard')
    else:
        user_form = RegisterForm()
        profile_form = HealthProfileForm()
        questionnaire_form = QuestionnaireForm()

    return render(request, 'dashboard/register_patient.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'questionnaire_form': questionnaire_form,
    })

@login_required
def patient_detail_asha(request, patient_id):
    patient_profile = get_object_or_404(UserProfile, id=patient_id)
    try:
        health_profile = HealthProfile.objects.get(patient=patient_profile.user)
        all_reports = []
        for q in health_profile.questionnaires.order_by('-submitted_at'):
            try:
                all_reports.append({
                    'questionnaire': q,
                    'report': q.report,
                })
            except RiskReport.DoesNotExist:
                pass
    except HealthProfile.DoesNotExist:
        health_profile = None
        all_reports = []

    return render(request, 'dashboard/patient_detail.html', {
        'patient_profile': patient_profile,
        'health_profile': health_profile,
        'all_reports': all_reports,
    })

@login_required
@role_required('doctor')
def doctor_dashboard(request):
    all_patient_profiles = UserProfile.objects.filter(
        role='patient'
    ).select_related('user')

    # Filters from URL query params
    risk_filter = request.GET.get('risk', '')
    district_filter = request.GET.get('district', '')
    search_query = request.GET.get('search', '')

    patients_data = []
    for profile in all_patient_profiles:
        try:
            health_profile = HealthProfile.objects.get(patient=profile.user)
            latest_q = health_profile.questionnaires.latest('submitted_at')
            report = latest_q.report
        except (HealthProfile.DoesNotExist, Questionnaire.DoesNotExist,
                RiskReport.DoesNotExist):
            report = None

        # Apply risk filter
        if risk_filter and report:
            if risk_filter == 'low' and report.overall_score >= 30:
                continue
            elif risk_filter == 'moderate' and not (30 <= report.overall_score < 60):
                continue
            elif risk_filter == 'high' and report.overall_score < 60:
                continue

        # Apply district filter
        if district_filter and profile.district.lower() != district_filter.lower():
            continue

        # Apply search filter
        if search_query:
            full_name = profile.user.get_full_name().lower()
            phone = profile.phone.lower()
            if search_query.lower() not in full_name and search_query.lower() not in phone:
                continue

        patients_data.append({
            'profile': profile,
            'report': report,
        })

    # Unique districts for filter dropdown
    districts = UserProfile.objects.filter(
        role='patient'
    ).values_list('district', flat=True).distinct()

    return render(request, 'dashboard/doctor_dashboard.html', {
        'patients_data': patients_data,
        'risk_filter': risk_filter,
        'district_filter': district_filter,
        'search_query': search_query,
        'districts': districts,
        'total': len(patients_data),
    })


@login_required
@role_required('doctor')
def doctor_patient_detail(request, patient_id):
    patient_profile = get_object_or_404(UserProfile, id=patient_id)

    try:
        health_profile = HealthProfile.objects.get(patient=patient_profile.user)
        all_reports = []
        for q in health_profile.questionnaires.order_by('-submitted_at'):
            try:
                all_reports.append({
                    'questionnaire': q,
                    'report': q.report,
                })
            except RiskReport.DoesNotExist:
                pass
    except HealthProfile.DoesNotExist:
        health_profile = None
        all_reports = []

    # Mark as reviewed and doctor notes added
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        notes = request.POST.get('doctor_notes', '')
        try:
            report = RiskReport.objects.get(id=report_id)
            report.reviewed_by_doctor = True
            report.doctor_notes = notes
            report.save()

            AuditLog.objects.create(
                action='mark_reviewed',
                performed_by=request.user,
                patient=patient_profile.user,
                details=f"Report reviewed. Notes: {notes}"
            )
            
            messages.success(request, "Notes saved and patient marked as reviewed.")
        except RiskReport.DoesNotExist:
            pass
        return redirect('doctor_patient_detail', patient_id=patient_id)

    return render(request, 'dashboard/doctor_patient_detail.html', {
        'patient_profile': patient_profile,
        'health_profile': health_profile,
        'all_reports': all_reports,
    })