"""
MediTrack — Streamlit Frontend

"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="MediTrack", page_icon="🏥", layout="wide")
st.title("🏥 MediTrack — Hospital Management System")
st.caption("*Manage patients, doctors, appointments, and prescriptions — all in one place.*")

def api_get(path, params=None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Can't reach the API. Is `uvicorn main:app --reload` running?")
        st.stop()
    except requests.exceptions.HTTPError:
        st.error(r.json().get("detail", f"Request failed ({r.status_code})"))
        return None


def api_post(path, payload):
    r = requests.post(f"{API_URL}{path}", json=payload, timeout=5)
    if r.status_code >= 400:
        try:
            st.error(r.json().get("detail", "Request failed"))
        except ValueError:
            st.error(f"Request failed ({r.status_code})")
        return None
    return r.json()


def api_delete(path):
    r = requests.delete(f"{API_URL}{path}", timeout=5)
    if r.status_code >= 400:
        st.error(r.json().get("detail", "Request failed"))
        return False
    return True


def api_patch(path, params=None):
    r = requests.patch(f"{API_URL}{path}", params=params, timeout=5)
    if r.status_code >= 400:
        st.error(r.json().get("detail", "Request failed"))
        return False
    return True


tabs = st.tabs(["Departments", "Doctors", "Patients", "Medicines", "Appointments", "Prescriptions"])

# ==================== DEPARTMENTS ====================
with tabs[0]:
    st.subheader("Add Department")
    with st.form("add_department", clear_on_submit=True):
        name = st.text_input("Department Name")
        if st.form_submit_button("Add Department") and name:
            result = api_post("/departments", {"name": name})
            if result:
                st.success(f"Added department: {name}")
                st.rerun()

    st.subheader("All Departments")
    departments = api_get("/departments") or []
    st.dataframe(departments, use_container_width=True)

# ==================== DOCTORS ====================
with tabs[1]:
    departments = api_get("/departments") or []
    dept_options = {d["name"]: d["department_id"] for d in departments}

    st.subheader("Register Doctor")
    if not dept_options:
        st.warning("Add a department first — doctors need a department to belong to.")
    else:
        with st.form("add_doctor", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                specialization = st.text_input("Specialization")
                email = st.text_input("Email (optional)")
            with col2:
                department_name = st.selectbox("Department", options=dept_options.keys())
                years_experience = st.number_input("Years of Experience", min_value=0, step=1)

            if st.form_submit_button("Add Doctor"):
                payload = {
                    "full_name": full_name,
                    "specialization": specialization,
                    "email": email or None,
                    "department_id": dept_options[department_name],
                    "years_experience": years_experience,
                }
                result = api_post("/doctors", payload)
                if result:
                    st.success(f"Added Dr. {full_name}")
                    st.rerun()

    st.subheader("All Doctors")
    doctors = api_get("/doctors") or []
    st.dataframe(doctors, use_container_width=True)

    if doctors:
        st.subheader("Deactivate a Doctor")
        doctor_labels = {f'{d["full_name"]} (id {d["doctor_id"]})': d["doctor_id"] for d in doctors}
        selected = st.selectbox("Select doctor", options=doctor_labels.keys(), key="deact_doc")
        if st.button("Deactivate Doctor"):
            if api_delete(f"/doctors/{doctor_labels[selected]}"):
                st.success("Doctor deactivated")
                st.rerun()

# ==================== PATIENTS ====================
with tabs[2]:
    st.subheader("Register Patient")
    with st.form("add_patient", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", key="p_name")
            dob = st.date_input("Date of Birth")
            gender = st.selectbox("Gender", options=["male", "female", "other"])
        with col2:
            email = st.text_input("Email (optional)", key="p_email")
            blood_group = st.text_input("Blood Group (optional)")

        if st.form_submit_button("Add Patient"):
            payload = {
                "full_name": full_name,
                "date_of_birth": str(dob),
                "gender": gender,
                "email": email or None,
                "blood_group": blood_group or None,
            }
            result = api_post("/patients", payload)
            if result:
                st.success(f"Registered {full_name}")
                st.rerun()

    st.subheader("All Patients")
    patients = api_get("/patients") or []
    search = st.text_input("Search by name")
    filtered = [p for p in patients if search.lower() in p["full_name"].lower()] if search else patients
    st.dataframe(filtered, use_container_width=True)

    if patients:
        st.subheader("Deactivate a Patient")
        patient_labels = {f'{p["full_name"]} (id {p["patient_id"]})': p["patient_id"] for p in patients}
        selected = st.selectbox("Select patient", options=patient_labels.keys(), key="deact_pat")
        if st.button("Deactivate Patient"):
            if api_delete(f"/patients/{patient_labels[selected]}"):
                st.success("Patient deactivated")
                st.rerun()

# ==================== MEDICINES ====================
with tabs[3]:
    st.subheader("Add Medicine")
    with st.form("add_medicine", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Medicine Name")
        with col2:
            unit_price = st.number_input("Unit Price", min_value=0.0, step=0.5)
        with col3:
            stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)

        if st.form_submit_button("Add Medicine"):
            payload = {"name": name, "unit_price": unit_price, "stock_quantity": stock_quantity}
            result = api_post("/medicines", payload)
            if result:
                st.success(f"Added {name}")
                st.rerun()

    st.subheader("All Medicines")
    medicines = api_get("/medicines") or []
    st.dataframe(medicines, use_container_width=True)

    st.subheader("Low Stock Alert")
    threshold = st.slider("Threshold", min_value=0, max_value=500, value=20)
    low_stock = api_get("/medicines/low-stock", params={"threshold": threshold}) or []
    if low_stock:
        st.warning(f"{len(low_stock)} medicine(s) below {threshold} units")
        st.dataframe(low_stock, use_container_width=True)
    else:
        st.success("No medicines below threshold")

# ==================== APPOINTMENTS ====================
with tabs[4]:
    doctors = api_get("/doctors") or []
    patients = api_get("/patients") or []
    doctor_options = {f'Dr. {d["full_name"]} ({d["specialization"]})': d["doctor_id"] for d in doctors}
    patient_options = {p["full_name"]: p["patient_id"] for p in patients}

    st.subheader("Book Appointment")
    if not doctor_options or not patient_options:
        st.warning("Add at least one doctor and one patient first.")
    else:
        with st.form("book_appointment", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                patient_name = st.selectbox("Patient", options=patient_options.keys())
                doctor_name = st.selectbox("Doctor", options=doctor_options.keys())
            with col2:
                appt_date = st.date_input("Date")
                appt_time = st.time_input("Time")

            if st.form_submit_button("Book Appointment"):
                payload = {
                    "patient_id": patient_options[patient_name],
                    "doctor_id": doctor_options[doctor_name],
                    "appointment_date": str(appt_date),
                    "appointment_time": appt_time.strftime("%H:%M:%S"),
                }
                result = api_post("/appointments", payload)
                if result:
                    st.success("Appointment booked")
                    st.rerun()
                # if the doctor is already booked at that slot, api_post already
                # displayed the backend's "Doctor already booked at this time" error

    st.subheader("All Appointments")
    appointments = api_get("/appointments") or []
    st.dataframe(appointments, use_container_width=True)

    if appointments:
        st.subheader("Update Appointment Status")
        appt_labels = {f'#{a["appointment_id"]} — {a["appointment_date"]} {a["appointment_time"]}': a["appointment_id"]
                       for a in appointments}
        selected = st.selectbox("Select appointment", options=appt_labels.keys())
        new_status = st.selectbox("New Status", options=["scheduled", "completed", "cancelled", "no_show"])
        if st.button("Update Status"):
            if api_patch(f"/appointments/{appt_labels[selected]}/status", params={"status": new_status}):
                st.success("Status updated")
                st.rerun()

# ==================== PRESCRIPTIONS ====================
with tabs[5]:
    appointments = api_get("/appointments") or []
    medicines = api_get("/medicines") or []
    completed_appts = [a for a in appointments if a.get("status") == "completed"]
    appt_options = {f'#{a["appointment_id"]} — {a["appointment_date"]}': a["appointment_id"] for a in completed_appts}
    medicine_options = {m["name"]: m["medicine_id"] for m in medicines}

    st.subheader("Create Prescription")
    if not appt_options:
        st.info("No completed appointments yet — mark an appointment 'completed' in the Appointments tab first.")
    elif "presc_items" not in st.session_state:
        st.session_state.presc_items = []

    if appt_options:
        selected_appt = st.selectbox("Appointment", options=appt_options.keys())
        notes = st.text_area("Notes (optional)")

        st.markdown("**Add medicines to this prescription:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            med_name = st.selectbox("Medicine", options=medicine_options.keys(), key="med_select")
        with col2:
            dosage = st.text_input("Dosage (e.g. 500mg)", key="dosage_input")
        with col3:
            frequency = st.number_input("Times/day", min_value=1, step=1, key="freq_input")
        with col4:
            duration = st.number_input("Duration (days)", min_value=1, step=1, key="dur_input")

        if st.button("Add Medicine to List"):
            if dosage:
                st.session_state.presc_items.append({
                    "medicine_id": medicine_options[med_name],
                    "medicine_name": med_name,
                    "dosage": dosage,
                    "frequency_per_day": frequency,
                    "duration_days": duration,
                })
            else:
                st.warning("Enter a dosage first")

        if st.session_state.get("presc_items"):
            st.write("Medicines added so far:")
            st.table(st.session_state.presc_items)

            if st.button("Submit Full Prescription", type="primary"):
                payload = {
                    "appointment_id": appt_options[selected_appt],
                    "notes": notes or None,
                    "medicines": [
                        {k: v for k, v in item.items() if k != "medicine_name"}
                        for item in st.session_state.presc_items
                    ],
                }
                result = api_post("/prescriptions", payload)
                if result:
                    st.success("Prescription created")
                    st.session_state.presc_items = []
                    st.rerun()

    st.subheader("All Prescriptions")
    prescriptions = api_get("/prescriptions") or []
    st.dataframe(prescriptions, use_container_width=True)