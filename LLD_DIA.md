# LLD: Data Flow & Process Diagrams (DFD)

## 1. Risk Assessment Process Flow
This diagram shows the end-to-end data processing when a user submits their health data.

```mermaid
flowchart TD
    Start[User Submits Form] --> Validate[Form Validation]
    Validate -->|Success| FetchProfile[Fetch Health Profile]
    FetchProfile --> RiskEngine[Invoke Risk Engine]
    
    subgraph "Risk Engine Processing"
        RiskEngine --> ML{ML Model Ready?}
        ML -- Yes --> Predict[Predict Diabetes Prob]
        ML -- No --> Heuristic[Apply Heuristic Weights]
        Predict --> Combine[Combine with Hypertension/Heart logic]
        Heuristic --> Combine
    end
    
    Combine --> Save[Save Risk Report]
    Save --> Notify[Display Success & Results]
```

## 2. Data Flow Diagram (Level 1)
```mermaid
graph LR
    User -->|Health Data| QuestionnaireApp[Questionnaire App]
    QuestionnaireApp -->|Raw Metrics| MLService[ML Prediction Service]
    MLService -->|Probabilities| ReportGenerator[Report Generator]
    ReportGenerator -->|Final Report| User
    ReportGenerator -->|Stored Results| DB[(Database)]
```
