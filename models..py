from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime, Date, NUMERIC, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base
import datetime

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

    department = relationship("Departments", back_populates="doctors")

class Patients(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key= True, autoincrement=True)
    full_name = Column(String, nullable= False)
    date_of_birth = Column(Date, nullable= False)
    gender = Column(String, nullable= False, default = None)
    email = Column(String, unique=True, default= None)
    blood_group = Column(String, nullable= True, default= None)
    is_active = Column(Boolean, nullable= False, default= True)
    created_at = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)

class Departments(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key= True, autoincrement= True)
    name = Column(String, nullable= False, unique= True)

    doctors = relationship("Doctors", back_populates="departments")

class Appointments(Base):
    __tablename__ = "appointments"
    appointment_id = Column(Integer, primary_key= True, nullable= False, autoincrement= True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id', nullable = False))
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'))
    appointment_date = Column(Date, nullable= False)
    appointment_time = Column(DateTime, nullable= False)
    status = Column(String, nullable= False, default = "Scheduled")

    patients = relationship("Patients", back_populates="appointments")
    doctors = relationship("Doctors", back_populates="appointments")

class Medicines(Base):
    __tablename__ = "medicines"
    medicine_id = Column(Integer, primary_key = True, nullable = False, autoincrement= True)
    name = Column(String, nullable= None, unique= True)
    unit_price = Column(NUMERIC, nullable= False, default=0.0)
    stock_quantity = Column(Integer, nullable=False,default= 0)


class Prescriptions(Base):
    __tablename__ = "prescriptions"
    prescription_id = Column(Integer, primary_key= True, nullable= True, autoincrement= True)
    appointment_id = Column(Integer, ForeignKey('appointments.appointment_id'), nullable= False, unique= True)
    notes = Column(String, nullable = True, default = True)
    created_at = Column(TIMESTAMP, nullable = False, default = DateTime)

    appointmemts = relationship("Appointments", backref= "prescriptions")


class Prescription_medicines(Base):
    __tablename__ = "prescriptions_medicines"
    id = Column(Integer, primary_key= True, nullable = False, autoincrement= True)
    prescription_id = Column(Integer, ForeignKey('prescription.prescription_id'), nullable= False)
    medicine_id = Column(Integer, ForeignKey('medicine.medicine_id'), nullable= False)
    dosage = Column(String, nullable= False)
    frequency_per_day = Column(Integer, nullable= False)
    duration_days = Column(Integer, nullable = False)

    prescription = relationship("Prescriptions", backref= "prescriptions_medicines")
    prescription = relationship("Medicine", backref= "prescriptions_medicines")