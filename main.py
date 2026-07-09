from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, Base, get_db
import models
import schemas

Base.metadata.create_all(engine)

app = FastAPI()

# ---------------- DOCTORS ----------------

@app.post("/doctors", response_model=schemas.doctors_out)
def create_doctor(doctor: schemas.doctors_in, db: Session = Depends(get_db)):
    new_doctor = models.Doctors(**doctor.model_dump())
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

@app.get("/doctors", response_model=list[schemas.doctors_out])
def list_doctors(db: Session = Depends(get_db)):
    return db.query(models.Doctors).filter(models.Doctors.is_active == True).all()

@app.get("/doctors/{doctor_id}", response_model=schemas.doctors_out)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctors).filter(models.Doctors.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctors).filter(models.Doctors.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_active = False
    db.commit()
    return {"message": "Doctor deactivated"}


# ---------------- DEPARTMENTS ----------------

@app.post("/departments", response_model=schemas.departments_out)
def create_department(department: schemas.departments_in, db: Session = Depends(get_db)):
    new_department = models.Departments(**department.model_dump())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department

@app.get("/departments", response_model=list[schemas.departments_out])
def list_departments(db: Session = Depends(get_db)):
    return db.query(models.Departments).all()

@app.get("/departments/{department_id}", response_model=schemas.departments_out)
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(models.Departments).filter(models.Departments.department_id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


# ---------------- PATIENTS ----------------

@app.post("/patients", response_model=schemas.patients_out)
def create_patient(patient: schemas.patients_in, db: Session = Depends(get_db)):
    new_patient = models.Patients(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get("/patients", response_model=list[schemas.patients_out])
def list_patients(db: Session = Depends(get_db)):
    return db.query(models.Patients).filter(models.Patients.is_active == True).all()

@app.get("/patients/{patient_id}", response_model=schemas.patients_out)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patients).filter(models.Patients.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patients).filter(models.Patients.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.is_active = False  # soft delete — preserves visit history
    db.commit()
    return {"message": "Patient deactivated"}

# ---------------- MEDICINES ----------------

@app.post("/medicines", response_model=schemas.medicine_out)
def create_medicine(medicine: schemas.medicine_in, db: Session = Depends(get_db)):
    new_medicine = models.Medicines(**medicine.model_dump())
    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)
    return new_medicine

@app.get("/medicines", response_model=list[schemas.medicine_out])
def list_medicines(db: Session = Depends(get_db)):
    return db.query(models.Medicines).all()

@app.get("/medicines/low-stock", response_model=list[schemas.medicine_out])
def low_stock_medicines(threshold: int = 20, db: Session = Depends(get_db)):
    return db.query(models.Medicines).filter(models.Medicines.stock_quantity < threshold).all()


# ---------------- APPOINTMENTS ----------------

@app.post("/appointments", response_model=schemas.appointments_out)
def create_appointment(appointment: schemas.appointments_in, db: Session = Depends(get_db)):
    # Conflict check + insert happen as one unit of work before commit.
    conflict = db.query(models.Appointments).filter(
        models.Appointments.doctor_id == appointment.doctor_id,
        models.Appointments.appointment_date == appointment.appointment_date,
        models.Appointments.appointment_time == appointment.appointment_time,
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Doctor already booked at this time")

    new_appointment = models.Appointments(**appointment.model_dump(), status="scheduled")
    try:
        db.add(new_appointment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Doctor already booked at this time")
    db.refresh(new_appointment)
    return new_appointment

@app.get("/appointments", response_model=list[schemas.appointments_out])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointments).all()

@app.patch("/appointments/{appointment_id}/status")
def update_appointment_status(appointment_id: int, status: str, db: Session = Depends(get_db)):
    appointment = db.query(models.Appointments).filter(models.Appointments.appointment_id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = status
    db.commit()
    return {"message": f"Appointment {appointment_id} marked {status}"}


# ---------------- PRESCRIPTIONS ----------------

@app.post("/prescriptions", response_model=schemas.prescriptions_out)
def create_prescription(payload: schemas.prescriptions_create_full, db: Session = Depends(get_db)):
    appointment = db.query(models.Appointments).filter(
        models.Appointments.appointment_id == payload.appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    new_prescription = models.Prescriptions(
        appointment_id=payload.appointment_id, notes=payload.notes
    )
    db.add(new_prescription)

    try:
        db.flush()  # assigns prescription_id without committing yet

        for item in payload.medicines:
            medicine = db.query(models.Medicines).filter(
                models.Medicines.medicine_id == item.medicine_id
            ).first()
            if not medicine:
                raise HTTPException(status_code=404, detail=f"Medicine id {item.medicine_id} not found")
            if medicine.stock_quantity <= 0:
                raise HTTPException(status_code=400, detail=f"{medicine.name} is out of stock")

            db.add(models.Prescription_medicines(
                prescription_id=new_prescription.prescription_id,
                medicine_id=item.medicine_id,
                dosage=item.dosage,
                frequency_per_day=item.frequency_per_day,
                duration_days=item.duration_days,
            ))
            medicine.stock_quantity -= 1

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create prescription")

    db.refresh(new_prescription)
    return new_prescription

@app.get("/prescriptions", response_model=list[schemas.prescriptions_out])
def list_prescriptions(db: Session = Depends(get_db)):
    return db.query(models.Prescriptions).all()