# ==============================
# IMPORTS
# ==============================
from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
import math

# ==============================
# APP INITIALIZATION (Q1)
# ==============================
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Medical Appointment System"}

# ==============================
# DATA (Q2)
# ==============================
doctors = [
    {"id": 1, "name": "Dr. Sharma", "specialization": "Cardiology", "fee": 500, "is_available": True},
    {"id": 2, "name": "Dr. Mehta", "specialization": "Dermatology", "fee": 300, "is_available": True},
    {"id": 3, "name": "Dr. Rao", "specialization": "Neurology", "fee": 700, "is_available": False},
    {"id": 4, "name": "Dr. Gupta", "specialization": "Orthopedic", "fee": 400, "is_available": True},
    {"id": 5, "name": "Dr. Khan", "specialization": "General", "fee": 200, "is_available": True},
    {"id": 6, "name": "Dr. Singh", "specialization": "Pediatrics", "fee": 350, "is_available": False},
]

appointments = []
appointment_counter = 1

# ==============================
# GET APIs (Q2–Q5)
# ==============================
@app.get("/doctors")
def get_doctors():
    return {"total": len(doctors), "data": doctors}

@app.get("/doctors/summary")
def summary():
    available = [d for d in doctors if d["is_available"]]
    unavailable = [d for d in doctors if not d["is_available"]]
    specializations = list(set([d["specialization"] for d in doctors]))

    return {
        "total": len(doctors),
        "available": len(available),
        "unavailable": len(unavailable),
        "specializations": specializations
    }

@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doc = next((d for d in doctors if d["id"] == doctor_id), None)
    if not doc:
        return {"error": "Doctor not found"}
    return doc

@app.get("/appointments")
def get_appointments():
    return {"total": len(appointments), "data": appointments}

# ==============================
# PYDANTIC MODEL (Q6)
# ==============================
class AppointmentRequest(BaseModel):
    patient_name: str = Field(min_length=2)
    doctor_id: int = Field(gt=0)
    slot: str = Field(min_length=3)
    symptoms: str = Field(min_length=5)
    appointment_type: str = "normal"

class NewDoctor(BaseModel):
    name: str = Field(min_length=2)
    specialization: str = Field(min_length=2)
    fee: int = Field(gt=0)
    is_available: bool = True

# ==============================
# HELPERS (Q7)
# ==============================
def find_doctor(doctor_id):
    return next((d for d in doctors if d["id"] == doctor_id), None)

def calculate_fee(base_fee, appointment_type):
    if appointment_type == "emergency":
        return base_fee + 200
    return base_fee

# ==============================
# POST APPOINTMENT (Q8–Q9)
# ==============================
@app.post("/appointments")
def book_appointment(req: AppointmentRequest):
    global appointment_counter

    doctor = find_doctor(req.doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}

    if not doctor["is_available"]:
        return {"error": "Doctor not available"}

    appointment = {
        "appointment_id": appointment_counter,
        "patient_name": req.patient_name,
        "doctor_id": req.doctor_id,
        "slot": req.slot,
        "fee": calculate_fee(doctor["fee"], req.appointment_type),
        "status": "booked"
    }

    appointments.append(appointment)
    appointment_counter += 1

    return appointment

# ==============================
# FILTER (Q10)
# ==============================
@app.get("/doctors/filter")
def filter_doctors(
    specialization: str = None,
    max_fee: int = None,
    is_available: bool = None
):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"] == specialization]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]

    return {"count": len(result), "data": result}

# ==============================
# CRUD (Q11–Q13)
# ==============================
@app.post("/doctors")
def add_doctor(new_doc: NewDoctor, response: Response):
    for d in doctors:
        if d["name"].lower() == new_doc.name.lower():
            return {"error": "Doctor already exists"}

    new_id = max([d["id"] for d in doctors]) + 1

    doctor = new_doc.dict()
    doctor["id"] = new_id

    doctors.append(doctor)
    response.status_code = 201
    return doctor

@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: int = None, is_available: bool = None):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}

    if fee is not None:
        doc["fee"] = fee
    if is_available is not None:
        doc["is_available"] = is_available

    return doc

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}

    doctors.remove(doc)
    return {"message": f"{doc['name']} deleted"}

# ==============================
# WORKFLOW (Q14–Q15)
# ==============================
queue = []

@app.post("/queue/add")
def add_queue(patient_name: str, doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}

    if doc["is_available"]:
        return {"message": "Doctor available, no queue needed"}

    queue.append({"patient": patient_name, "doctor_id": doctor_id})
    return {"message": "Added to queue"}

@app.get("/queue")
def get_queue():
    return queue

@app.post("/complete/{appointment_id}")
def complete_appointment(appointment_id: int):
    appt = next((a for a in appointments if a["appointment_id"] == appointment_id), None)
    if not appt:
        return {"error": "Appointment not found"}

    appt["status"] = "completed"

    for q in queue:
        if q["doctor_id"] == appt["doctor_id"]:
            queue.remove(q)
            return {"message": "Completed and next patient notified"}

    return {"message": "Completed"}

# ==============================
# SEARCH (Q16)
# ==============================
@app.get("/doctors/search")
def search(keyword: str):
    result = [d for d in doctors if keyword.lower() in d["name"].lower() or keyword.lower() in d["specialization"].lower()]
    return {"total": len(result), "data": result} if result else {"message": "No results"}

# ==============================
# SORT (Q17)
# ==============================
@app.get("/doctors/sort")
def sort(sort_by: str = "fee", order: str = "asc"):
    if sort_by not in ["fee", "name", "specialization"]:
        return {"error": "Invalid sort_by"}

    reverse = True if order == "desc" else False
    sorted_data = sorted(doctors, key=lambda x: x[sort_by], reverse=reverse)

    return {"data": sorted_data}

# ==============================
# PAGINATION (Q18)
# ==============================
@app.get("/doctors/page")
def paginate(page: int = 1, limit: int = 3):
    total = len(doctors)
    start = (page - 1) * limit
    data = doctors[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": math.ceil(total / limit),
        "data": data
    }

# ==============================
# ORDER SEARCH + SORT (Q19)
# ==============================
@app.get("/appointments/search")
def search_appointments(name: str):
    result = [a for a in appointments if name.lower() in a["patient_name"].lower()]
    return result

@app.get("/appointments/sort")
def sort_appointments(order: str = "asc"):
    return sorted(appointments, key=lambda x: x["fee"], reverse=(order == "desc"))

# ==============================
# COMBINED (Q20)
# ==============================
@app.get("/doctors/browse")
def browse(
    keyword: str = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    data = doctors

    # filter
    if keyword:
        data = [d for d in data if keyword.lower() in d["name"].lower()]

    # sort
    data = sorted(data, key=lambda x: x[sort_by], reverse=(order == "desc"))

    # pagination
    total = len(data)
    start = (page - 1) * limit
    data = data[start:start + limit]

    return {
        "total": total,
        "page": page,
        "data": data
    }