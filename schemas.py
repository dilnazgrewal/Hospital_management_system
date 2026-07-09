from pydantic import BaseModel, EmailStr, ConfigDict
import datetime
from datetime import date
from enum import Enum
from typing import Optional

class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class Status(Enum):
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NOSHOW = 'no_show'

class doctors_in(BaseModel):
    full_name: str
    specialization: str
    email: Optional[str] = None
    department_id: int
    years_experience: int

class doctors_out(BaseModel):
    doctor_id: int
    full_name: str
    specialization: str
    email: Optional[EmailStr] = None
    department_id: int
    years_experience: int
    is_active: bool
    class Config:
        from_attributes = True

class departments_in(BaseModel):
    name: str

class departments_out(BaseModel):
    department_id: int
    name: str
    class Config:
        from_attributes = True

class patients_in(BaseModel):
    full_name: str
    date_of_birth: date
    gender: Gender
    email: Optional[str] = None
    blood_group: str

    model_config = ConfigDict(use_enum_values=True)

class patients_out(BaseModel):
    patient_id: int
    full_name: str
    date_of_birth: date
    gender: Gender
    email: Optional[str] = None
    blood_group: str
    is_active: bool
    created_at: datetime.datetime

    model_config = ConfigDict(use_enum_values=True)


class appointments_in(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: datetime.time
    model_config = ConfigDict(use_enum_values=True)

class appointments_out(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: datetime.time
    status: Status
    model_config = ConfigDict(use_enum_values=True)

class medicine_in(BaseModel):
    name: str
    unit_price: float
    stock_quantity: int

class medicine_out(BaseModel):
    medicine_id: int
    name: str
    unit_price: float
    stock_quantity: int
    class Config:
        from_attributes = True

class prescriptions_in(BaseModel):
    appointment_id: int
    notes: Optional[str] = None

class prescriptions_out(BaseModel):
    prescription_id: int
    appointment_id: int
    notes: Optional[str] = None
    class Config:
        from_attributes = True

class prescription_medicines_in(BaseModel):
    prescription_id: int
    medicine_id: int
    dosage: str
    frequency_per_day: int
    duration_days: int

class prescription_medicines_out(BaseModel):
    id: int
    prescription_id: int
    medicine_id: int
    dosage: str
    frequency_per_day: int
    duration_days: int
    class Config:
        from_attributes = True

class prescription_medicine_item(BaseModel):
    medicine_id: int
    dosage: str
    frequency_per_day: int
    duration_days: int

class prescriptions_create_full(BaseModel):
    appointment_id: int
    notes: Optional[str] = None
    medicines: list[prescription_medicine_item]


