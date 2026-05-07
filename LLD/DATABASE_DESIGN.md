# Low-Level Design: Database Design

## 1. Entity Relationship Diagram (ERD)
The database is designed to track patient profiles, their health questionnaire submissions, and the resulting risk reports.

```mermaid
erDiagram
    USER ||--|| HEALTH_PROFILE : "has"
    HEALTH_PROFILE ||--o{ QUESTIONNAIRE : "submits"
    QUESTIONNAIRE ||--|| RISK_REPORT : "generates"
    USER ||--o{ AUDIT_LOG : "triggers"
    
    HEALTH_PROFILE {
        int id
        int user_id
        int age
        string gender
        float weight_kg
        float height_cm
    }
    
    QUESTIONNAIRE {
        int id
        int profile_id
        datetime submitted_at
        string lifestyle_data
        boolean symptoms
        boolean family_history
    }
    
    RISK_REPORT {
        int id
        int questionnaire_id
        int overall_score
        float ml_probability
        string diabetes_risk
        string hypertension_risk
        string heart_risk
        text recommendations
    }
```

## 2. Data Models Detail
### 2.1 User & Health Profile
- **User**: Standard Django user model for authentication.
- **HealthProfile**: Stores static/semi-static patient information like Age, Gender, and BMI-related data.

### 2.2 Questionnaire & Risk Report
- **Questionnaire**: Captures point-in-time data from the user.
- **RiskReport**: Stores the output of the Risk Engine, including ML probabilities and heuristic-based scores.

## 3. Integrity Constraints
- Foreign keys ensure that reports are always linked to a valid questionnaire.
- Audit logs track all major changes for medical traceability.
