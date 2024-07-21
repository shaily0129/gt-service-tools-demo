from fastapi import FastAPI, HTTPException
from uuid import UUID, uuid4
from typing import List
from models import Patient, PatientUpdateRequest, Threshold

app = FastAPI()

# Initialize database with sample patients
db: List[Patient] = [
    Patient(
        id=uuid4(),
        name="Adrian Monk",
        external_hemorrhage=3,
        tension_pneumothorax=4,
        traumatic_brain_injury=6,
        burn=2,
        gcs=10,
        sbp=60,
        rr=20,
    ),
    Patient(
        id=uuid4(), name="Natalie Tieger", splenic_laceration=6, gcs=6, sbp=100, rr=40
    ),
    Patient(id=uuid4(), name="Leland Stottlemeyer", external_hemorrhage=5, burn=6),
    Patient(
        id=uuid4(),
        name="Jake Peralta",
        liver_hematoma=4,
        tension_pneumothorax=6,
        traumatic_brain_injury=4,
        burn=6,
        gcs=5,
        sbp=120,
        rr=88,
    ),
    Patient(id=uuid4(), name="Sharona Fleming", gcs=12, sbp=120, rr=89),
    Patient(
        id=uuid4(),
        name="Randy Disher",
        external_hemorrhage=5,
        tension_pneumothorax=6,
        traumatic_brain_injury=6,
        burn=2,
        gcs=15,
        sbp=80,
        rr=60,
    ),
    Patient(id=uuid4(), name="Trudy Monk", splenic_laceration=6, gcs=6, sbp=100, rr=40),
    Patient(id=uuid4(), name="Charles Kroger", external_hemorrhage=2, burn=1),
    Patient(
        id=uuid4(),
        name="Julie Trieger",
        liver_hematoma=1,
        tension_pneumothorax=1,
        traumatic_brain_injury=1,
        burn=1,
        gcs=4,
        sbp=40,
        rr=20,
    ),
    Patient(id=uuid4(), name="Benjy Fleming", gcs=12, sbp=120, rr=89),
]

# Thresholds for triage algorithm
thresholds_data_algo3 = {
    "external_hemorrhage": Threshold(min_value=1, max_value=6),
    "tension_pneumothorax": Threshold(min_value=1, max_value=6),
    "traumatic_brain_injury": Threshold(min_value=1, max_value=6),
    "concussion": Threshold(min_value=1, max_value=6),
    "cerebral_contusion": Threshold(min_value=1, max_value=6),
    "subarachnoid_hemorrhage": Threshold(min_value=1, max_value=6),
    "epidural_hematoma": Threshold(min_value=1, max_value=6),
    "nasal_fracture": Threshold(min_value=1, max_value=6),
    "orbital_fracture": Threshold(min_value=1, max_value=6),
    "le_fort_II_fracture": Threshold(min_value=1, max_value=6),
    "rib_fracture": Threshold(min_value=1, max_value=6),
    "lung_contusion": Threshold(min_value=1, max_value=6),
    "flail_chest": Threshold(min_value=1, max_value=6),
    "aortic_laceration": Threshold(min_value=1, max_value=6),
    "minor_liver_laceration": Threshold(min_value=1, max_value=6),
    "splenic_laceration": Threshold(min_value=1, max_value=6),
    "liver_hematoma": Threshold(min_value=1, max_value=6),
    "pancreatic_transection": Threshold(min_value=1, max_value=6),
    "radius_ulna_fracture": Threshold(min_value=1, max_value=6),
    "femur_fracture": Threshold(min_value=1, max_value=6),
    "knee_dislocation": Threshold(min_value=1, max_value=6),
    "traumatic_amputation_below_knee": Threshold(min_value=1, max_value=6),
    "traumatic_amputation_above_knee": Threshold(min_value=1, max_value=6),
    "burn": Threshold(min_value=1, max_value=6),
    "gcs": Threshold(min_value=3, max_value=15),
    "sbp": Threshold(min_value=0, max_value=219),
    "rr": Threshold(min_value=0, max_value=100),
}

def validate_patient(patient: Patient):
    for key, value in patient.dict().items():
        if key in thresholds_data_algo3 and value is not None:
            threshold = thresholds_data_algo3[key]
            if not (threshold.min_value <= value <= threshold.max_value):
                raise HTTPException(
                    status_code=400,
                    detail=f"{key} value {value} is out of range ({threshold.min_value}-{threshold.max_value})",
                )

@app.get("/api/v1/patients")
async def fetch_patients():
    return db

@app.post("/api/v1/patients")
async def register_patient(patient: Patient):
    validate_patient(patient)
    patient.id = uuid4()
    db.append(patient)
    return {"id": patient.id}

@app.delete("/api/v1/patients/{patient_id}")
async def delete_patient(patient_id: UUID):
    for patient in db:
        if patient.id == patient_id:
            db.remove(patient)
            return
    raise HTTPException(
        status_code=404, detail=f"Patient with id:{patient_id} does not exist"
    )

@app.put("/api/v1/patients/{patient_id}")
async def update_patient(patient_update: PatientUpdateRequest, patient_id: UUID):
    for patient in db:
        if patient.id == patient_id:
            update_data = patient_update.dict(exclude_unset=True)
            updated_patient = patient.copy(update=update_data)
            validate_patient(updated_patient)
            for key, value in update_data.items():
                if value is not None:
                    setattr(patient, key, value)
            return
    raise HTTPException(
        status_code=404, detail=f"Patient with id:{patient_id} does not exist"
    )

# @app.get("/api/v1/triage_scores")
# async def compute_triage_scores():
#     triage_algo = TriageFactory.create_triage_algo(
#         TriageAlgoName.LIFE, thresholds=thresholds_data_algo3
#     )
#     triage_scores = triage_algo.triage(db)
#     return {"triage_scores": triage_scores}
