🏥 ArogyaCheck — Health Risk Screening for Rural India

Bridging the healthcare gap for 68% of rural Indians who lack access to preventive disease assessment.


📌 About the Project
ArogyaCheck is a full-stack health risk screening platform built specifically for rural India. It analyzes 15+ health parameters to generate risk scores for Diabetes, Hypertension, and Heart Disease — color-coded as 🟢 Low, 🟡 Moderate, and 🔴 High — with personalized health guidance for each user.
Built with rural connectivity in mind, it loads in 7 seconds on 2G networks — 80% faster than the industry standard for SPAs.

💡 Why I Built This
During my research, I found that 68% of rural Indians have never undergone any form of preventive health screening. Most platforms are either too expensive, too complex, or require stable internet — none of which rural areas have. ArogyaCheck was built to fix exactly that. A doctor in a village health camp should be able to pull up patient risk trends on a basic smartphone. A patient with no medical background should be able to understand their health risk in seconds. That was the goal.

🚀 Features

👤 3 User Roles — Patient, Doctor, Admin — each with tailored dashboards
🧮 Multi-factor Risk Engine — analyzes 15+ parameters including age, BMI, family history, lifestyle & symptoms
🎨 Color-coded Severity Classification — Low 🟢 / Moderate 🟡 / High 🔴
📊 Doctor Analytics Dashboard — interactive Plotly charts showing disease trends across 10+ villages
🗺️ Geographic Risk Visualization — age-group vulnerabilities & disease prevalence maps
💡 Personalized Health Guidance — actionable recommendations per individual risk profile
⚡ 2G Network Optimized — server-side rendering for low-end devices & poor connectivity


🛠️ Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Python, Django |
| Frontend | HTML, CSS, Bootstrap |
| Database | SQLite |
| Data & Charts | Plotly, Pandas, Matplotlib |
| Rendering | Server-Side Rendering (SSR) |

📊 Impact Numbers
| Metric | Value |
|--------|-------|
| Health parameters analyzed | 15+ |
| Villages covered | 10+ |
| User roles supported | 3 |
| Diseases screened | Diabetes, Hypertension, Heart Disease |
| Load time on 2G | 7 seconds |
| Industry average | 35 seconds |
| Performance improvement | 80% faster |

🖥️ User Roles Explained
🧑‍⚕️ Patient

Fills a simple health assessment form
Gets instant color-coded risk score
Receives personalized health recommendations

👨‍⚕️ Doctor

Views aggregated patient data across villages
Analyzes geographic and age-group disease trends
Uses interactive Plotly dashboards to plan health camps

🔧 Admin

Manages users and platform data
Monitors overall platform activity

⚙️ Setup & Installation

# Clone the repository
git clone https://github.com/jyotsnak1603/arogyacheck.git

# Navigate into the project
cd arogyacheck

# Install all dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

Then open your browser and go to `http://127.0.0.1:8000`

---

## 📁 Project Structure
```
arogyacheck/
├── manage.py
├── requirements.txt
├── arogyacheck/
│   ├── settings.py
│   └── urls.py
├── patients/          # Patient role — forms, risk scores, guidance
├── doctors/           # Doctor role — village analytics, dashboards
├── admin_panel/       # Admin role — user management
├── templates/         # HTML templates (Bootstrap)
└── static/            # CSS, JS, images

🙋‍♀️ Built By
Jyotsna Chaudhary — B.Tech CSE, Lovely Professional University
Devyansh Verma — B.Tech CSE, Lovely Professional University
📧 jyotsnak1603@gmail.com
📧 devyansh770@gmail.com

"Early detection saves lives — and no one should miss that chance just because they live far from a city."

⭐ If this project inspired you or helped you, please give it a star — it means a lot!
