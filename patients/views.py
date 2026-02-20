from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthProfile, Questionnaire, RiskReport
from .forms import HealthProfileForm, QuestionnaireForm
from .risk_engine import calculate_risk

@login_required
def questionnaire_view(request):
    #Get or creat health profile for patient
    try:
        health_profile = HealthProfile.objects.get(patient=request.user)
        profile_exists = True
    except HealthProfile.DoesNotExist:
        health_profile = None
        profile_exists = False

    if request.method == 'POST':
        if not profile_exists:
            # First time — save health profile first
            profile_form = HealthProfileForm(request.POST)
            questionnaire_form = QuestionnaireForm(request.POST)
            if profile_form.is_valid() and questionnaire_form.is_valid():
                # Save health profile
                health_profile = profile_form.save(commit=False)
                health_profile.patient = request.user
                health_profile.save()
                # Save questionnaire
                questionnaire = questionnaire_form.save(commit=False)
                questionnaire.health_profile = health_profile
                questionnaire.save()
                # Generate risk report
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
                messages.success(request, "Questionnaire submitted successfully!")
                return redirect('report')
        else:
            # Profile exists — only save questionnaire
            questionnaire_form = QuestionnaireForm(request.POST)
            profile_form = HealthProfileForm(instance=health_profile)
            if questionnaire_form.is_valid():
                questionnaire = questionnaire_form.save(commit=False)
                questionnaire.health_profile = health_profile
                questionnaire.save()
                # Generate risk report
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
                messages.success(request, "Questionnaire submitted successfully!")
                return redirect('report')
    else:
        profile_form = HealthProfileForm(
            instance=health_profile if profile_exists else None
        )
        questionnaire_form = QuestionnaireForm()

    return render(request, 'patients/questionnaire.html', {
        'profile_form': profile_form,
        'questionnaire_form': questionnaire_form,
        'profile_exists': profile_exists,
    })


@login_required
def report_view(request):
    try:
        health_profile = HealthProfile.objects.get(patient=request.user)
        # Get latest questionnaire and its report
        latest_questionnaire = health_profile.questionnaires.latest('submitted_at')
        report = latest_questionnaire.report
    except (HealthProfile.DoesNotExist, Questionnaire.DoesNotExist,
            RiskReport.DoesNotExist):
        messages.error(request, "No report found. Please fill the questionnaire first.")
        return redirect('questionnaire')

    return render(request, 'patients/report.html', {
        'report': report,
        'health_profile': health_profile,
        'questionnaire': latest_questionnaire,
    })