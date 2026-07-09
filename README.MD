# 🏥 MediTrack — Hospital Management System

A relational database project for managing patients, doctors, appointments, medicines, and prescriptions in a small clinic/hospital — built to practice **database design, SQLAlchemy ORM, and backend logic** using FastAPI and PostgreSQL.

> Built as a hands-on, project-first way to learn relational databases — normalized schema, real foreign keys, transactions, and cascade rules, not just theory.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the App](#running-the-app)
- [API Endpoints](#api-endpoints)
- [Design Decisions](#design-decisions)
- [Learning Outcomes](#learning-outcomes)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Overview

MediTrack solves a simple but real problem: small clinics often manage patients, doctor schedules, and prescriptions through paper registers or disconnected spreadsheets, leading to duplicate records, double-booked doctors, and lost prescription history.

MediTrack stores all of this in a single, normalized relational database — every entity (patient, doctor, appointment, medicine, prescription) is properly connected through foreign keys and relationships, exposed through a FastAPI backend and a Streamlit UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL (SQLite supported for local dev) |
| Data Validation | Pydantic |
| Frontend | Streamlit |
| Language | Python 3.10+ |

---

## Features

- Full CRUD for Patients, Doctors, Departments, Medicines, Appointments, and Prescriptions
- **Double-booking prevention** — a doctor cannot be booked for two appointments at the same date/time, enforced both at the transaction level and with a database `UNIQUE` constraint
- **Soft delete** for Patients and Doctors — records are deactivated (`is_active = False`), never hard-deleted, preserving medical history
- **Transactional prescription creation** — a prescription and all of its medicine entries are saved atomically; if any medicine fails validation, nothing is partially saved
- **Low-stock medicine alerts**
- Many-to-many relationship between Prescriptions and Medicines via an association table carrying dosage, frequency, and duration
- Streamlit dashboard for managing every resource without needing to touch `/docs`

---

## Database Schema

Seven normalized tables (3NF):

| Table | Purpose |
|---|---|
| `departments` | Hospital departments (Cardiology, Pediatrics, etc.) |
| `doctors` | Doctor details, linked to a department |
| `patients` | Patient demographic and contact details |
| `appointments` | Links a patient and doctor at a specific date/time |
| `medicines` | Medicine catalog with stock and pricing |
| `prescriptions` | One prescription per completed appointment |
| `prescription_medicines` | Association table — medicines attached to a prescription, with dosage/frequency/duration |

### Relationships

- **Department → Doctors** — one-to-many
- **Doctor → Appointments** — one-to-many
- **Patient → Appointments** — one-to-many
- **Appointment → Prescription** — one-to-one (enforced via a `UNIQUE` FK)
- **Prescription ↔ Medicines** — many-to-many (via `prescription_medicines`, modeled as a full association object since it carries its own data)

### Cascade Rules

| Relationship | Behavior | Reasoning |
|---|---|---|
| Appointment → Prescription | `cascade="all, delete-orphan"` | A prescription cannot exist without its appointment |
| Prescription → Prescription_medicines | `cascade="all, delete-orphan"` | Medicine entries have no meaning without their prescription |
| Doctor / Patient deletion | Soft delete only | Medical and appointment history must be preserved |
| Medicine deletion | Soft delete (`is_discontinued`) | Old prescriptions must still reference the medicine |

---

## Project Structure

```
meditrack/
│
├── main.py              # FastAPI app and all route definitions
├── database.py           # engine, SessionLocal, Base, get_db()
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic request/response schemas
├── .gitignore
├── app.py                  # Streamlit frontend
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/gurpartapxen/meditrack.git
cd meditrack
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary>requirements.txt</summary>

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
streamlit
requests
python-dotenv
```
</details>

### 4. Configure the database

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://username:password@localhost:5432/meditrack_db
```

For local development without PostgreSQL, `database.py` falls back to SQLite automatically if `DATABASE_URL` isn't set.


## Running the App

You need **two terminals** — the API and the UI run as separate processes.

**Terminal 1 — start the backend:**
```bash
uvicorn main:app --reload
```
API available at `http://127.0.0.1:8000`
Interactive docs at `http://127.0.0.1:8000/docs`

**Terminal 2 — start the frontend:**
```bash
streamlit run app.py
```
UI available at `http://localhost:8501`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/departments` | Create a department |
| `GET` | `/departments` | List all departments |
| `POST` | `/doctors` | Register a doctor |
| `GET` | `/doctors` | List active doctors |
| `GET` | `/doctors/{id}` | Get a single doctor |
| `DELETE` | `/doctors/{id}` | Deactivate a doctor (soft delete) |
| `POST` | `/patients` | Register a patient |
| `GET` | `/patients` | List active patients |
| `GET` | `/patients/{id}` | Get a single patient |
| `DELETE` | `/patients/{id}` | Deactivate a patient (soft delete) |
| `POST` | `/medicines` | Add a medicine |
| `GET` | `/medicines` | List all medicines |
| `GET` | `/medicines/low-stock` | List medicines below a stock threshold |
| `POST` | `/appointments` | Book an appointment (conflict-checked) |
| `GET` | `/appointments` | List all appointments |
| `PATCH` | `/appointments/{id}/status` | Update appointment status |
| `POST` | `/prescriptions` | Create a prescription with medicines (transactional) |
| `GET` | `/prescriptions` | List all prescriptions |

Full interactive documentation is available at `/docs` once the server is running.

---

## Design Decisions

A few deliberate choices worth calling out, since they were made for reasons rather than by default:

- **Soft delete over hard delete** for Patients and Doctors — a hospital should never lose medical history because a record was "removed."
- **`prescription_medicines` as a full model, not a plain junction table** — because it carries meaningful data (dosage, frequency, duration) beyond just two foreign keys.
- **Conflict checking + insert wrapped in one transaction** for appointment booking — plus a database-level `UNIQUE(doctor_id, appointment_date, appointment_time)` constraint as a second line of defense against race conditions.
- **Prescription creation is atomic** — the prescription and every one of its medicine entries succeed or fail together, so a prescription is never left with a partial medicine list.

---

## Learning Outcomes

This project was built to practice, hands-on:

- Designing a normalized (3NF) relational schema
- Primary keys, foreign keys, and composite `UNIQUE` constraints
- One-to-many, one-to-one, and many-to-many relationships in SQLAlchemy
- `relationship()` and `back_populates` configuration
- Cascade rules (`delete-orphan`) vs. soft-delete, chosen per real-world meaning
- Multi-step database transactions with `rollback()`
- Building a REST API with FastAPI + Pydantic on top of SQLAlchemy
- Migrating from SQLite to PostgreSQL with a single connection-string change

---

## Future Improvements

- Authentication and role-based access (admin / doctor / front-desk)
- Alembic migrations for schema versioning
- Automated tests (pytest) for booking conflicts and cascade behavior
- Email/SMS appointment reminders
- Deployment (Railway/Render) with a hosted PostgreSQL instance

---

## Author

**Dilnaz Kaur Grewal**
GitHub: [@dilnazgrewal](https://github.com/dilnazgrewal)

---

## License

This project is open source and available under the [MIT License](LICENSE).