"""
Unit tests for ArogyaCheck patients application.
Covers health profile calculations and risk engine logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import HealthProfile, Questionnaire, RiskReport
from .risk_engine import calculate_risk

class PatientModelTest(TestCase):
    """Tests for patient-related models."""

    def setUp(self):
        self.user = User.objects.create_user(username='testpatient', password='password123')
        self.profile = HealthProfile.objects.create(
            patient=self.user,
            age=25,
            gender='male',
            weight_kg=70.0,
            height_cm=175.0
        )

    def test_bmi_calculation(self):
        """Verify BMI is calculated correctly: 70 / (1.75^2) ~= 22.86."""
        expected_bmi = round(70.0 / (1.75 ** 2), 2)
        self.assertEqual(self.profile.bmi(), expected_bmi)

    def test_profile_str(self):
        """Verify the string representation of HealthProfile."""
        self.assertEqual(str(self.profile), "testpatient - Age 25")

class RiskEngineTest(TestCase):
    """Tests for the risk calculation logic."""

    def setUp(self):
        self.user = User.objects.create_user(username='risktest', password='password123')
        self.profile = HealthProfile.objects.create(
            patient=self.user,
            age=50,  # Older age increases risk
            gender='female',
            weight_kg=95.0,
            height_cm=160.0  # Obese BMI increases risk
        )
        self.questionnaire = Questionnaire.objects.create(
            health_profile=self.profile,
            physical_activity='none',
            diet_type='non_veg',
            smoking=True,
            alcohol=True,
            sleep_hours=5,
            frequent_thirst=True,
            family_diabetes=True,
            already_hypertensive=True
        )

    def test_high_risk_calculation(self):
        """Verify that a high-risk profile returns the correct risk levels."""
        results = calculate_risk(self.questionnaire, self.profile)
        
        # Given age 50, BMI ~37 (obese), smoking, and symptoms, risk should be High
        self.assertEqual(results['diabetes_risk'], 'high')
        self.assertEqual(results['hypertension_risk'], 'high')
        self.assertTrue(results['refer_for_test'])
        self.assertIn("immediately", results['recommendation'])

    def test_low_risk_calculation(self):
        """Verify that a healthy profile returns Low risk."""
        healthy_user = User.objects.create_user(username='healthy', password='password123')
        healthy_profile = HealthProfile.objects.create(
            patient=healthy_user,
            age=20,
            gender='female',
            weight_kg=55.0,
            height_cm=165.0
        )
        healthy_q = Questionnaire.objects.create(
            health_profile=healthy_profile,
            physical_activity='heavy',
            diet_type='vegetarian',
            smoking=False,
            alcohol=False,
            sleep_hours=8
        )
        
        results = calculate_risk(healthy_q, healthy_profile)
        self.assertEqual(results['diabetes_risk'], 'low')
        self.assertFalse(results['refer_for_test'])
