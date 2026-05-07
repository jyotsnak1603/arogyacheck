# High-Level Design (HLD)

## 1. System Overview
ArogyaCheck is a monolithic Django application designed for high availability in low-bandwidth scenarios.

## 2. Architecture Diagram

```mermaid
graph TD
    User((User/Patient)) -->|Browser| Frontend[HTML/Bootstrap/JS]
    Frontend -->|HTTP Requests| Django[Django Backend]
    
    subgraph "Django Server"
        Views[Views/Controllers] --> Models[Models/ORM]
        Views --> RiskEngine[Risk Engine]
        RiskEngine --> MLModel[Random Forest Model]
    end
    
    Models -->|SQL| DB[(SQLite/Postgres)]
    RiskEngine -->|Report Data| Views
    Views -->|Rendered HTML| Frontend
```

## 3. Module Description
- **Accounts**: Manages user session and roles.
- **Patients**: Handles health data and the risk prediction logic.
- **Dashboard**: Aggregates data for clinical review.

Detailed architecture: [HLD/SYSTEM_ARCHITECTURE.md](HLD/SYSTEM_ARCHITECTURE.md)
