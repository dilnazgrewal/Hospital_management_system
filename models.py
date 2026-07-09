from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime, Date, NUMERIC, TIMESTAMP, Time
from sqlalchemy.orm import relationship
from database import Base
import datetime
from sqlalchemy import UniqueConstraint


class Doctors(Base):
    __tablename__ = "doctors"
    doctor_id = Column(Integer, primary_key= True, autoincrement=True)
    full_name = Column(String, nullable= False)
    specialization = Column(String, nullable= False)
    email = Column(String, unique=True, default= None)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable= False)
    years_experience = Column(Integer, nullable = True, default = 0)
    is_active = Column(Boolean, nullable= False, default= True)
    created_at = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)

    departments = relationship("Departments", back_populates="doctors")
    appointments = relationship("Appointments", back_populates="doctors")

class Patients(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key= True, autoincrement=True)
    full_name = Column(String, nullable= False)
    date_of_birth = Column(Date, nullable= False)
    gender = Column(String, nullable= True)
    email = Column(String, unique=True, default= None)
    blood_group = Column(String, nullable= True, default= None)
    is_active = Column(Boolean, nullable= False, default= True)
    created_at = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)

    appointments = relationship("Appointments", back_populates="patients")

class Departments(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key= True, autoincrement= True)
    name = Column(String, nullable= False, unique= True)

    doctors = relationship("Doctors", back_populates="departments")

class Appointments(Base):
    __tablename__ = "appointments"
    appointment_id = Column(Integer, primary_key= True, nullable= False, autoincrement= True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable = False)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'), nullable= False)
    appointment_date = Column(Date, nullable= False)
    appointment_time = Column(Time, nullable= False)
    status = Column(String, nullable= False, default = "scheduled")

    patients = relationship("Patients", back_populates="appointments")
    doctors = relationship("Doctors", back_populates="appointments")
    prescriptions = relationship("Prescriptions", back_populates="appointments", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time'),)

class Medicines(Base):
    __tablename__ = "medicines"
    medicine_id = Column(Integer, primary_key = True, nullable = False, autoincrement= True)
    name = Column(String, nullable= False, unique= True)
    unit_price = Column(NUMERIC, nullable= False, default=0.0)
    stock_quantity = Column(Integer, nullable=False,default= 0)

    prescriptions_medicines = relationship("Prescription_medicines", back_populates= "medicines")

class Prescriptions(Base):
    __tablename__ = "prescriptions"
    prescription_id = Column(Integer, primary_key= True, autoincrement= True)
    appointment_id = Column(Integer, ForeignKey('appointments.appointment_id'), nullable= False, unique= True)
    notes = Column(String, nullable = True)
    created_at = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)

    appointments = relationship("Appointments", back_populates= "prescriptions")
    prescriptions_medicines = relationship("Prescription_medicines", back_populates= "prescriptions", cascade="all, delete-orphan")


class Prescription_medicines(Base):
    __tablename__ = "prescriptions_medicines"
    id = Column(Integer, primary_key= True, nullable = False, autoincrement= True)
    prescription_id = Column(Integer, ForeignKey('prescriptions.prescription_id'), nullable= False)
    medicine_id = Column(Integer, ForeignKey('medicines.medicine_id'), nullable= False)
    dosage = Column(String, nullable= False)
    frequency_per_day = Column(Integer, nullable= False)
    duration_days = Column(Integer, nullable = False)

    prescriptions = relationship("Prescriptions", back_populates= "prescriptions_medicines")
    medicines = relationship("Medicines", back_populates= "prescriptions_medicines")

    __table_args__ = (UniqueConstraint('prescription_id', 'medicine_id'),)
