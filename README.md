# BOSS (Branch Operations Support System)
### Preliminary Screening Committee (PSC) & Standing Advisory Committee (SAC) Review Portal

A Django-based web application for managing branch operations registries, PSC/SAC workflows, checklists, and role matrices. 

---

## 🛠️ System Requirements
- **Python**: 3.9
- **Database**: 
  - SQLite (Local development)
  - PostgreSQL (KBL environment)
- **Key Python packages**: `Django==3.1.2`, `ldap3` (for AD authentication), `pycryptodome` (for login cryptography), and dependencies listed in `requirements.txt`.

---

## 💻 Running the App in Local Environment (No KBL LDAP / Local Database Mode)

To run the application locally without KBL Active Directory (LDAP) and using local SQLite databases:

### 1. Setup Virtual Environment & Install Dependencies
```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
.\venv\Scripts\activate.bat

# Install required packages
pip install -r requirements.txt
```

  ./kblpsc_env39/Scripts/python.exe -m pytest tests/