"""
Integration and Unit tests for ArogyaCheck patients application.
Moved to centralized tests directory for better project structure.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from patients.models import HealthProfile, Questionnaire, RiskReport
from patients.risk_engine import calculate_risk

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
            age=50,
            gender='female',
            weight_kg=95.0,
            height_cm=160.0
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
        self.assertEqual(results['diabetes_risk'], 'high')
        self.assertEqual(results['hypertension_risk'], 'high')

class IntegrationTest(TestCase):
    """Simple integration test to verify the flow."""
    def test_end_to_end_risk_flow(self):
        # 1. Create user and profile
        user = User.objects.create_user(username='e2e', password='password123')
        profile = HealthProfile.objects.create(patient=user, age=30, gender='male', weight_kg=75, height_cm=180)
        
        # 2. Submit questionnaire
        q = Questionnaire.objects.create(
            health_profile=profile, 
            physical_activity='moderate', 
            diet_type='vegetarian',
            sleep_hours=8,
            smoking=False,
            alcohol=False
        )
        
        # 3. Calculate risk
        results = calculate_risk(q, profile)
        
        # 4. Verify results structure
        self.assertIn('diabetes_risk', results)
        self.assertIn('overall_score', results)
