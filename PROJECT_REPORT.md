# ArogyaCheck Project Report

## Cover Page

**Project Title:** arogyacheck

**Type:** AI-Powered Health Diagnostic Platform

**Repository:** arogyacheck-main

**Prepared For:** Rural Health Infrastructure & Predictive Analytics

**Prepared By:** ArogyaCheck Development Team

**Date:** May 6, 2026

---

## Introduction

ArogyaCheck is a robust health diagnostic platform designed to provide early screening for lifestyle diseases like Diabetes, Hypertension, and Cardiovascular conditions. The platform is specifically optimized for rural and low-connectivity environments where access to medical specialists is limited. It uses a hybrid approach, combining Machine Learning (Random Forest) with clinical heuristic weights to ensure reliability even when data is sparse.

## Project Overview

ArogyaCheck bridges the healthcare gap by providing an accessible, low-bandwidth tool for quantifying health risks. It centralizes patient profiling, health questionnaires, and risk reporting in a single Django-based ecosystem.

### Key Features

- **Machine Learning Risk Prediction**: Powered by a Random Forest model trained on the Pima Indians dataset.
- **Hybrid Risk Engine**: Combines ML predictions with clinical heuristic weights for multi-condition screening.
- **Color-Coded Risk Indicators**: Instant visual feedback (Low, Moderate, High) for better user understanding.
- **2G Network Optimized**: Server-Side Rendering (SSR) ensures fast performance on weak networks.
- **Patient Dashboard**: Interactive visualizations of health trends using Plotly.
- **Role-Based Access**: Dedicated flows for Patients, Doctors, and Administrators.

### Technologies Used

- **Framework**: Django 5.2.11
- **Machine Learning**: Scikit-learn (Random Forest), NumPy, Pandas
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: Bootstrap 5, Vanilla CSS (Glassmorphism), JavaScript
- **Visualization**: Plotly
- **Environment**: `python-dotenv` for configuration

### Project Structure

The application is organized into specialized modules:

- `accounts`: User authentication, registration, and profile management.
- `patients`: Core health logic, health profiles, questionnaires, and risk engine.
- `dashboard`: Visualization and summary reporting.
- `config`: Project-wide settings and URL configuration.
- `HLD/`: High-Level Design documentation.
- `LLD/`: Low-Level Design documentation.
- `tests/`: Centralized test suite.

### Installation Summary

To run the application locally:

1. Create and activate a virtual environment: `python -m venv venv`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure environment variables (refer to `.env.template`).
4. Run migrations: `python manage.py migrate`.
5. Start the server: `python manage.py runserver`.

### Usage Summary

- **Public Site**: `http://localhost:8000/`
- **Admin Interface**: `http://localhost:8000/admin/`
- **Patients**: Register, complete health profiles, and submit risk assessments.
- **Doctors**: Review patient risk reports and provide clinical recommendations.

### Configuration Summary

Key environment variables:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DATABASE_URL` (if using production DB)
- `ML_MODEL_PATH`

### Feature Details

#### Hybrid Risk Engine
- Utilizes Random Forest for high-accuracy Diabetes prediction.
- Falls back to heuristic weights (Age, BMI, Smoking) for Hypertension and Cardiac risks.
- Normalizes scores into actionable risk categories.

#### Rural Optimization (SSR)
- Minimizes client-side JavaScript execution.
- Leverages Django templates for fast initial page load on 2G/3G networks.

## Problem Statement

In many developing regions, "silent killer" diseases go undiagnosed until they reach critical stages. High-bandwidth medical portals often fail on 2G/3G networks, and rural populations lack the tools to quantify their health risks before clinical intervention is required. Manual record-keeping leads to data silos and poor long-term health tracking.

## Existing System Analysis

Current systems often rely on heavy JavaScript frameworks that fail in low-connectivity zones or generic health blogs that lack personalized risk quantification. There is a lack of integration between predictive AI and clinical heuristics at the primary care level in rural clinics. ArogyaCheck improves on this by centralizing the diagnostic workflow and making risks visible and actionable.

## Requirements

### Functional Requirements
1. Users must be able to register and manage their health profiles.
2. The system must process health questionnaires and generate risk reports.
3. The ML engine must predict diabetes probability based on input metrics.
4. The system must provide color-coded visual feedback for risk levels.
5. Doctors must be able to view patient history and reports.

### Non-Functional Requirements
1. **Performance**: Page load times must be optimized for low-bandwidth (SSR).
2. **Security**: Sensitive health data must be protected through role-based access.
3. **Scalability**: The risk engine should be modular to allow adding new disease models.
4. **Reliability**: The system must handle cases where ML components are temporarily unavailable.

### Hardest Requirement
The most challenging aspect is balancing ML predictive accuracy with the performance constraints of rural network optimization, ensuring that complex model inferences don't degrade the user experience on low-end devices.

## Design

### Rough Design Before Coding
The system was architected around a monolithic MVT structure for simplicity and performance. The data model centers on the `HealthProfile`, which acts as the anchor for all longitudinal patient data.

### High Level Diagrams
- System architecture and module flow: [HLD.md](HLD.md)
- LLD flow diagrams: [LLD_DIA.md](LLD_DIA.md)
- UML diagrams: [LLD_UML.md](LLD_UML.md)
- Low-level design notes: [LLD.md](LLD.md)

### Data Models
Documented in [LLD/DATABASE_DESIGN.md](LLD/DATABASE_DESIGN.md).
- **User**: Custom auth.
- **HealthProfile**: Age, Gender, BMI data.
- **Questionnaire**: Point-in-time symptoms and lifestyle data.
- **RiskReport**: ML probability and heuristic outputs.

### System Architecture
Detailed in [HLD/SYSTEM_ARCHITECTURE.md](HLD/SYSTEM_ARCHITECTURE.md).

## Testing Implementation
The project includes a centralized test suite under [tests/](tests/) and a guide in [tests.md](tests.md).

### Test Files
- Patient logic tests: [tests/test_patients.py](tests/test_patients.py)
- Accounts/Auth tests: (Coming soon)

## User Manual
Refer to [USER_MANUAL.md](USER_MANUAL.md) for a step-by-step guide.

## Source Code
- Settings: [config/settings.py](config/settings.py)
- Risk Engine: [patients/risk_engine.py](patients/risk_engine.py)
- Models: [patients/models.py](patients/models.py)

## References
- Django: https://docs.djangoproject.com/
- Scikit-learn: https://scikit-learn.org/
- Project Diagrams: [HLD.md](HLD.md), [LLD.md](LLD.md)
