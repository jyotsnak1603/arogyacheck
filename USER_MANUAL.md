# User Manual: ArogyaCheck Platform

## 1. Installation Guide
1. **Virtual Environment**: Create a virtual environment using `python -m venv venv` and activate it.
2. **Dependencies**: Install the required packages with `pip install -r requirements.txt`.
3. **Environment**: Copy `.env.template` to `.env` and fill in the required keys.
4. **Database**: Run `python manage.py migrate` to set up the database schema.
5. **Admin User**: Create an administrator with `python manage.py createsuperuser`.
6. **Run**: Start the server with `python manage.py runserver`.

## 2. Operating the Platform

### For Patients
1. **Register**: Sign up for an account and log in.
2. **Profile**: Fill in your basic health profile (Age, Gender, Height, Weight).
3. **Assessment**: Navigate to "New Assessment" and fill in the questionnaire.
4. **Report**: View your instant risk report and follow the recommendations.

### For Doctors/Admins
1. **Dashboard**: Log in to the professional dashboard to see an overview of patient health trends.
2. **Review**: Access detailed risk reports for individual patients.
3. **Configuration**: Use the Django Admin at `/admin` to manage risk weights and system parameters.

## 3. Understanding Risk Levels
- 🟢 **Low Risk**: No immediate action required. Maintain healthy habits.
- 🟡 **Moderate Risk**: Caution advised. Consider professional consultation.
- 🔴 **High Risk**: Immediate medical attention is recommended.

## 4. Troubleshooting
- **Database Errors**: Ensure SQLite/Postgres is properly configured in `.env`.
- **ML Model Missing**: Verify that the `.joblib` files exist in `patients/ml/models/`.
- **Styling Issues**: Clear your browser cache or ensure `static` files are collected.
