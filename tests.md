# Project Testing Infrastructure

## 1. Overview
ArogyaCheck uses a robust testing suite to ensure the accuracy of the risk engine and the integrity of user data.

## 2. Test Structure
The tests are organized in the root `tests/` directory:
- `test_patients.py`: Unit and integration tests for the patient health risk logic.
- `__init__.py`: Package initialization.

## 3. How to Run Tests
### Using Django Test Runner:
```bash
python manage.py test tests
```

### Using Pytest (Recommended for detailed reports):
```bash
pytest
```

## 4. Coverage Areas
- **Model Integrity**: Ensuring BMI and other profile metrics are calculated correctly.
- **Risk Engine Accuracy**: Verifying that ML and heuristic logic correctly categorize risks (Low/Moderate/High).
- **Authentication**: Testing secure access to patient dashboards.

## 5. Continuous Integration
Tests should be run before every deployment to ensure no regressions in the risk calculation logic.
