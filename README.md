# Employee Retention Support System

### An Enterprise Explainable AI & Longitudinal Workforce Signal Engine

The Employee Retention Support System is an explainable AI-based workforce decision-support platform designed to help organizations identify employees who may benefit from supportive retention conversations.

The system analyzes synthetic employee data such as engagement, tenure, workload, career growth, and compensation. It helps managers and HR teams understand workforce trends and prioritize supportive actions through transparent, human-reviewed assessments.

## Key Features

- Employee management and profile tracking.
- Employee engagement and workload analysis.
- Compensation and career growth tracking.
- Explainable support-priority scores with HIGH, MEDIUM, and LOW levels.
- Employee retention workbench.
- Supportive intervention and follow-up tracking.
- Team and role management.
- Analytics dashboard and workforce trends.
- Data-quality validation and audit logs.
- Role-Based Access Control (RBAC).
- Historical employee data tracking.
- Synthetic data generation with reproducible results.

## Technology Stack

**Backend**
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Alembic
- JWT Authentication
- bcrypt
- Psycopg

**Frontend**
- React
- Vite
- Tailwind CSS
- Axios
- Recharts
- Lucide React

**Testing**
- Pytest
- FastAPI TestClient

## System Architecture

The application follows a three-layer architecture:

- **Frontend:** React provides the user interface, dashboards, and visualizations.
- **Backend:** FastAPI handles REST APIs, authentication, business logic, and explainable assessments.
- **Database:** PostgreSQL stores employee information, historical snapshots, assessments, interventions, and audit records.

## Project Folder Structure

```text
Hackathon/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── data/
│   ├── tests/
│   ├── .env
│   ├── .env.example
│   ├── alembic.ini
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── layouts/
│   │   └── pages/
│   │
│   ├── .env
│   ├── package.json
│   ├── index.html
│   └── vite.config.js
│
└── README.md
```

**Folder descriptions:**

- `backend/app/core/` – Application configuration, security, and authentication.
- `backend/app/database/` – Database connection and session management.
- `backend/app/models/` – SQLAlchemy database models.
- `backend/app/routers/` – FastAPI API endpoints.
- `backend/app/schemas/` – Pydantic request and response schemas.
- `backend/app/services/` – Business logic and assessment services.
- `backend/data/` – Synthetic dataset and generated data files.
- `backend/scripts/` – Data generation and utility scripts.
- `backend/tests/` – Automated backend tests.
- `frontend/src/api/` – Frontend API integration.
- `frontend/src/components/` – Reusable UI components.
- `frontend/src/context/` – Application state and authentication context.
- `frontend/src/layouts/` – Application layouts.
- `frontend/src/pages/` – Application pages and dashboards.

## Frontend Screens

The application provides the following screens:

- **Login and Registration:** User authentication and account registration.
- **Dashboard:** Overview of workforce metrics, support priorities, and analytics.
- **Retention Workbench:** Displays employees requiring supportive attention.
- **Employee Directory:** Search and view employee information.
- **Employee Profile:** Displays employee details and historical workforce timeline.
- **Teams:** View teams, departments, and team memberships.
- **Roles:** Manage job classifications and role information.
- **Engagement:** View quarterly employee engagement information.
- **Workload:** Track workload patterns and overtime signals.
- **Compensation:** View compensation bands and career progression information.
- **Interventions:** Record supportive conversations, action items, and follow-ups.
- **Analytics:** Visualize workforce trends and support-priority distribution.
- **Data Quality:** Review validation runs and data-quality issues.
- **Administration:** Manage users, permissions, and administrative activities.
- **Audit Logs:** Review important system activities.

## Demo Accounts

The login page provides quick-fill demo accounts for different organizational roles.

- **System Admin:** `sys_admin`
- **HR Partner:** `hr_partner_1`
- **Team Manager:** `manager_apollo`
- **IT/Ops Partner:** `it_ops_lead`

Additional employee and auditor accounts may be available depending on the configured database and seeded users.

Use the locally configured demo passwords. Passwords and authentication secrets are intentionally not published in this README.

## Explainable Assessment

The system evaluates multiple workforce signals, including:

- Workload and overtime patterns.
- Employee engagement changes.
- Career growth and promotion history.
- Compensation compared with the assigned salary band.

It generates a support-priority score and explains the factors behind the assessment.

Missing voluntary surveys are treated neutrally, and temporary planned workload increases are distinguished from sustained workload strain.

The assessment supports constructive conversations. It does not make employment decisions or represent a definitive probability of resignation.

## Data Governance and Ethical AI

- Uses synthetic employee data for demonstration and testing.
- Separates historical assessment features from later attrition outcomes.
- Prevents future-data leakage.
- Preserves employee team and role history.
- Does not penalize employees for missing voluntary survey responses.
- Supports human review before any intervention.
- Maintains audit records for important system activities.
- Avoids using sensitive personal attributes for support-priority assessments.

## User Roles

The application supports different access levels:

- System Administrator
- HR Partner
- Team Manager
- IT/Ops Partner
- Employee
- Auditor

Each role has access according to its assigned permissions.

## Installation and Setup

### 1. Start PostgreSQL

Ensure PostgreSQL is running and the required database is configured.

### 2. Start the Backend

Open Command Prompt:

```cmd
cd /d C:\CandidateWorkspace\Hackathon\backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Start the Frontend

Open another Command Prompt:

```cmd
cd /d C:\CandidateWorkspace\Hackathon\frontend
npm run dev
```

## Application URLs

- **Frontend Application:** http://localhost:5173
- **Swagger API Documentation:** http://localhost:8000/docs

## Testing

Run backend tests using:

```cmd
cd /d C:\CandidateWorkspace\Hackathon\backend
.venv\Scripts\activate
python -m pytest tests -v
```

The backend test suite previously completed successfully with 48 passed tests.

## Synthetic Dataset

The project uses a reproducible synthetic dataset with:

- 10,000 synthetic employees.
- 24 months of historical data.
- Eight quarterly snapshots from 2024 Q1 to 2025 Q4.
- Fixed random seed: `20261022`.
- Separate simulated attrition outcomes for testing and validation.

## Limitations

- **Synthetic Data:** The application uses simulated employee data and does not represent actual organizational workforce information.
- **Support-Priority Scores:** Scores are based on defined assessment rules and should not be interpreted as exact resignation probabilities.
- **Human Review Required:** Assessments are intended to support conversations, not replace human judgment.
- **Data Quality Dependency:** Incomplete or inaccurate input data can affect the quality of assessments and analytics.
- **No Automated Employment Decisions:** The system does not make hiring, firing, promotion, or other adverse employment decisions.
- **Local Demo Configuration:** Database credentials, environment variables, and demo accounts must be configured before running the application.
- **Production Deployment:** Additional security, privacy, fairness, monitoring, backup, and access-control reviews are required before real-world use.

## Future Enhancements

- Advanced workforce trend analysis.
- Improved dashboard visualizations.
- Additional data-quality checks.
- Enhanced reporting and export capabilities.
- Improved notification and follow-up workflows.
- Further security and deployment improvements.

## Conclusion

The Employee Retention Support System combines explainable analytics, historical workforce data, and human-centered decision support to help organizations improve employee engagement and retention practices responsibly.