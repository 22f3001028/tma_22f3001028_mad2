# Trekking Management Application V2

An academic project built with Flask, Vue.js, SQLite, and Redis.

## Project Overview

The Trekking Management Application (TMA) helps adventure organizations
manage trekking activities. It supports three roles:

- **Admin** — manages treks, staff, users, and views reports
- **Trek Staff** — manages assigned treks and participants  
- **User/Trekker** — browses treks, makes bookings, views history

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Vue.js 3, Bootstrap 5, Axios |
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended |
| Database | SQLite (programmatically created) |
| Caching | Redis |
| Background Jobs | Celery + Celery Beat |
| Email | Flask-Mail (Gmail SMTP) |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 22+
- Redis (Memurai for Windows)

### 1. Clone / Extract the project

```bash
cd trekking_management_app
```

### 2. Backend setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start Flask
cd backend
python app.py
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Redis
Start Memurai from the Start Menu (Windows) or run:
```bash
sudo service redis-server start   # Linux/WSL
```

### 5. Celery (for email jobs only)

Open two additional terminals with venv active:

```bash
# Terminal 3 - Worker
cd backend
python -m celery -A celery_app.celery worker --loglevel=info --pool=solo

# Terminal 4 - Beat scheduler
python -m celery -A celery_app.celery beat --loglevel=info
```

---

## Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@tma.com | admin123 |
| Staff | Created by Admin | Set by Admin |
| User | Register via app | Set during registration |

---

## Key Features

- Role-based access control (Admin / Staff / User)
- Trek creation, assignment, and status management
- Booking system with overbooking and duplicate prevention
- Redis caching for open treks with auto-expiry (5 minutes)
- CSV export of booking history
- Daily email reminders for upcoming treks (Celery Beat)
- Monthly activity report emailed to Admin (Celery Beat)
- Search and filter treks by name, location, difficulty
- Staff restricted to managing only their assigned treks
- Complete trekking history per user

---

## AI/LLM Declaration

This project was developed with AI assistance (Claude by Anthropic).

The following components were implemented personally by the student
as required by the project specification:

- Authentication system (`models/user.py`, `routes/auth.py`)
- Trek model (`models/trek.py`)

All other components were built with AI guidance and reviewed,
understood, and tested by the student.