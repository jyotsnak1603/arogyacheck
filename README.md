# ArogyaCheck: Early Health Risk Prediction Platform

## 📖 Introduction
ArogyaCheck is a robust health diagnostic platform designed to provide early screening for lifestyle diseases like Diabetes, Hypertension, and Cardiovascular conditions. The platform is specifically optimized for rural and low-connectivity environments where access to medical specialists is limited.

## ⚠️ Problem Statement
In many developing regions, "silent killer" diseases go undiagnosed until they reach critical stages. High-bandwidth medical portals often fail on 2G/3G networks, and rural populations lack the tools to quantify their health risks before clinical intervention is required.

## 💡 Solution
ArogyaCheck bridges this gap by:
1. **Hybrid Analytics**: Combining Machine Learning (Random Forest) with clinical heuristic weights.
2. **Rural Optimization**: Using Server-Side Rendering (SSR) to ensure fast load times on weak networks.
3. **Actionable Guidance**: Providing instant, color-coded risk reports and referrals.

## 🏗️ Architecture & Design
- **High-Level Design**: [HLD.md](HLD.md) | [System Architecture](HLD/SYSTEM_ARCHITECTURE.md)
- **Low-Level Design**: [LLD.md](LLD.md) | [Database Design](LLD/DATABASE_DESIGN.md)
- **Diagrams**: [LLD_DIA.md](LLD_DIA.md) (Flow) | [LLD_UML.md](LLD_UML.md) (Class/Seq)
- **Technical Specs**: Django, Scikit-learn, Bootstrap.

## 📄 Project Documentation
- **[PROJECT_REPORT.md](PROJECT_REPORT.md)**: Comprehensive summary of the project.
- **[USER_MANUAL.md](USER_MANUAL.md)**: Guide for end-users and administrators.
- **[MILESTONES.md](MILESTONES.md)**: Project roadmap and current status.

## 🛠️ Installation & Setup
1. **Clone the repo**
2. **Create Venv**: `python -m venv venv`
3. **Install Deps**: `pip install -r requirements.txt`
4. **Run Server**: `python manage.py runserver`

## 🧪 Testing
Run the comprehensive test suite:
```bash
python manage.py test tests
```
For more details, see **[tests.md](tests.md)**.
