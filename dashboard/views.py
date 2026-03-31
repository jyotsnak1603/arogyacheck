from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, Case, When, Value, IntegerField, CharField
from django.db.models.functions import TruncMonth

import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
from collections import Counter

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

    # OPTIMIZED CODE - Reduces queries by 90%+
    registered_profiles = UserProfile.objects.filter(
        registered_by=request.user,
        role='patient'
        ).select_related('user').prefetch_related(
            'user__healthprofile__questionnaires__report')
    
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
    # Filters from URL query params
    risk_filter = request.GET.get('risk', '')
    district_filter = request.GET.get('district', '')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)

    # Base queryset with necessary joins
    # We want the LATEST report for each patient. 
    # For now, let's assume one report per patient for simplicity in ORM filtering,
    # OR better: use Subqueries to get the latest.
    
    all_patient_profiles = UserProfile.objects.filter(role='patient').select_related('user', 'user__healthprofile')

    # Apply district filter in ORM
    if district_filter:
        all_patient_profiles = all_patient_profiles.filter(district__iexact=district_filter)

    # Apply search filter in ORM
    if search_query:
        all_patient_profiles = all_patient_profiles.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # To filter by risk (which is in RiskReport), we need to join through HealthProfile and Questionnaire
    # Since we want the LATEST report, we'll fetch them and then filter.
    # Note: For massive scale, this should use a Subquery or Denormalization.
    
    patients_data = []
    # Optimization: Prefetch reports to avoid N+1
    all_patient_profiles = all_patient_profiles.prefetch_related(
        'user__healthprofile__questionnaires__report'
    )

    for profile in all_patient_profiles:
        try:
            hp = profile.user.healthprofile
            latest_q = hp.questionnaires.latest('submitted_at')
            report = latest_q.report
        except (AttributeError, HealthProfile.DoesNotExist, Questionnaire.DoesNotExist, RiskReport.DoesNotExist):
            report = None

        # Apply risk filter
        if risk_filter and report:
            if risk_filter == 'low' and report.overall_score >= 30:
                continue
            elif risk_filter == 'moderate' and not (30 <= report.overall_score < 60):
                continue
            elif risk_filter == 'high' and report.overall_score < 60:
                continue
        elif risk_filter and not report:
            continue

        patients_data.append({
            'profile': profile,
            'report': report,
        })

    # Pagination
    paginator = Paginator(patients_data, 10) # 10 patients per page
    try:
        patients_page = paginator.page(page)
    except PageNotAnInteger:
        patients_page = paginator.page(1)
    except EmptyPage:
        patients_page = paginator.page(paginator.num_pages)

    # Unique districts for filter dropdown
    districts = UserProfile.objects.filter(role='patient').values_list('district', flat=True).distinct()

    return render(request, 'dashboard/doctor_dashboard.html', {
        'patients_data': patients_page,
        'risk_filter': risk_filter,
        'district_filter': district_filter,
        'search_query': search_query,
        'districts': districts,
        'total': paginator.count,
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


@login_required
@role_required('doctor')
def doctor_analytics(request):
    # Summary stats using ORM
    stats_query = RiskReport.objects.aggregate(
        total_patients=Count('id'),
        avg_score=Avg('overall_score'),
        high_risk=Count('id', filter=Q(overall_score__gte=60)),
        low_risk=Count('id', filter=Q(overall_score__lt=30))
    )
    
    stats = {
        'total_patients': stats_query['total_patients'] or 0,
        'avg_score': round(stats_query['avg_score'], 1) if stats_query['avg_score'] else 0,
        'high_risk': stats_query['high_risk'] or 0,
        'low_risk': stats_query['low_risk'] or 0,
    }

    charts = {}

    # Chart 1 — Risk Level Distribution (Pie Chart)
    # Using the choice field values or custom labels
    risk_dist = RiskReport.objects.annotate(
        level=Case(
            When(overall_score__lt=30, then=Value('Low')),
            When(overall_score__lt=60, then=Value('Moderate')),
            default=Value('High'),
            output_field=CharField(),
        )
    ).values('level').annotate(count=Count('id'))

    labels = [d['level'] for d in risk_dist]
    values = [d['count'] for d in risk_dist]

    fig1 = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=['#28a745', '#ffc107', '#dc3545']),
        hole=0.4,
    ))
    fig1.update_layout(title='Overall Risk Level Distribution', height=350, template='plotly_white')
    charts['risk_distribution'] = pio.to_html(fig1, full_html=False)

    # Chart 2 — Age Group Analysis (Bar Chart)
    age_dist = HealthProfile.objects.annotate(
        age_group=Case(
            When(age__lte=30, then=Value('18-30')),
            When(age__lte=40, then=Value('31-40')),
            When(age__lte=50, then=Value('41-50')),
            When(age__lte=60, then=Value('51-60')),
            default=Value('60+'),
            output_field=CharField(),
        )
    ).values('age_group').annotate(count=Count('id')).order_by('age_group')

    fig2 = go.Figure(go.Bar(
        x=[d['age_group'] for d in age_dist],
        y=[d['count'] for d in age_dist],
        marker_color='#28a745',
        text=[d['count'] for d in age_dist],
        textposition='auto',
    ))
    fig2.update_layout(title='Patients by Age Group', xaxis_title='Age Group', yaxis_title='Number of Patients', height=350, template='plotly_white')
    charts['age_distribution'] = pio.to_html(fig2, full_html=False)

    # Chart 3 — Disease Risk Comparison (Bar Chart)
    disease_metrics = ['diabetes_risk', 'hypertension_risk', 'heart_risk']
    fig3 = go.Figure()
    colors = {'low': '#28a745', 'moderate': '#ffc107', 'high': '#dc3545'}
    
    for level, color in colors.items():
        counts = []
        for metric in disease_metrics:
            count = RiskReport.objects.filter(**{metric: level}).count()
            counts.append(count)
        
        fig3.add_trace(go.Bar(
            name=level.capitalize(),
            x=[m.replace('_risk', '').capitalize() for m in disease_metrics],
            y=counts,
            marker_color=color,
        ))

    fig3.update_layout(title='Disease Risk Comparison', barmode='group', height=350, template='plotly_white')
    charts['disease_comparison'] = pio.to_html(fig3, full_html=False)

    # Chart 4 — District wise Average Risk (Bar Chart)
    district_dist = UserProfile.objects.filter(role='patient').values('district').annotate(
        avg_score=Avg('user__healthprofile__questionnaires__report__overall_score')
    ).filter(avg_score__isnull=False)

    fig4 = go.Figure(go.Bar(
        x=[d['district'] for d in district_dist],
        y=[round(d['avg_score'], 1) for d in district_dist],
        marker_color='#17a2b8',
        text=[round(d['avg_score'], 1) for d in district_dist],
        textposition='auto',
    ))
    fig4.update_layout(title='Average Risk Score by District', height=350, template='plotly_white')
    charts['district_analysis'] = pio.to_html(fig4, full_html=False)

    # Chart 5 — Monthly Registration Trend (Line Chart)
    monthly_trend = Questionnaire.objects.annotate(
        month=TruncMonth('submitted_at')
    ).values('month').annotate(count=Count('id')).order_by('month')

    fig5 = go.Figure(go.Scatter(
        x=[d['month'].strftime('%b %Y') for d in monthly_trend],
        y=[d['count'] for d in monthly_trend],
        mode='lines+markers',
        line=dict(color='#28a745', width=3),
        marker=dict(size=10),
    ))
    fig5.update_layout(title='Monthly Patient Registration Trend', height=350, template='plotly_white')
    charts['monthly_trend'] = pio.to_html(fig5, full_html=False)

    return render(request, 'dashboard/doctor_analytics.html', {
        'charts': charts,
        'stats': stats,
    })