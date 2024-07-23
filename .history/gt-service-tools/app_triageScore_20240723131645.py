from typing import Dict, List, Union, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
from caching.CacheRedis import RedisManager
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageScoreInteraction import (
    TriageScoreInteraction,
)
from services.models.Models import TriageInteractionRequest
from services.service_triage.factory.FactoryAlgoTriage import (
    Threshold,
    TriageAlgoName,
    TriageFactory,
)
from utils.Utils import load_env_file

 
class PatientParams(BaseModel):
    patient_id: str  # Mandatory field
    params: Optional[dict]  # Optional field

class PatientIdOnly(BaseModel):
    patient_id: str  # Mandatory field

class TriageRequestBody(BaseModel):
    request_id: str
    patients: List[Union[PatientParams, PatientIdOnly]]

class PatientRecord(BaseModel):
    request_id: str
    patient_id: str
    params: dict
    triage_score: Optional[Dict] = None

# Define thresholds_data_algo3
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

app = FastAPI(
    title="ASU Tools",
    description="Demo of using an interactive tools",
    version="0.0.1",
)


@app.post("/tools/triage", tags=["Triage"])
async def rate_response(
    request: Request, body: TriageRequestBody = Body(...)
) -> dict:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()

        results = []
        for patient in body.patients:


            if isinstance(patient, PatientParams):
                # Generate a unique key for each patient interaction
                key = f"tools-triage-{body.request_id}-{patient.patient_id}"

                # Create TriageInteractionRequest for each patient
                triage_interaction_request = TriageInteractionRequest(
                    request_id=body.request_id, patient_id=patient.patient_id, params=patient.params
                )
                # Check for new or complete interaction request
                cached_bir_json = caching_manager.get_json(key)
                if cached_bir_json is None:
                    caching_manager.save_json(key, triage_interaction_request.json())
                else:
                    cached_bir = TriageInteractionRequest(**cached_bir_json)
                    if cached_bir.complete:
                        results.append(cached_bir)
                        continue

                # Interaction request is still WIP, so run the triage algorithm and cache result
                bir = TriageScoreInteraction(thresholds=thresholds_data_algo3).run_triage_algo(
                    triage_interaction_request=triage_interaction_request
                )

                # Save the result and add to results
                caching_manager.save_json(key, bir.json())
                results.append(bir)

            elif isinstance(patient, PatientIdOnly):
                key = f"tools-triage-*{patient.patient_id}"
                cached_bir_json = caching_manager.get_json(key)
                if cached_bir_json:
                    cached_bir = TriageInteractionRequest(**cached_bir_json)
                    results.append(cached_bir)
        # Sort results by score
        sorted_results = sorted(results, key=lambda x: x.triage_score.score, reverse=True)

        return {"results": sorted_results}       

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/triage", tags=["Triage"])
async def get_all_patients() -> dict:
    try:
        load_env_file("dev.env")
        caching_manager = RedisManager()
        keys = caching_manager.get_keys("tools-triage-*")
        
        patients = []
        unique_patient_ids = set()
        for key in keys:
            cached_patient_json = caching_manager.get_json(key)
            if cached_patient_json:
                cached_patient = TriageInteractionRequest(**cached_patient_json)
                if cached_patient.patient_id not in unique_patient_ids:
                    unique_patient_ids.add(cached_patient.patient_id)
                    patient_record = {
                        "request_id": cached_patient.request_id,
                        "patient_id": cached_patient.patient_id,
                        "params": cached_patient.params,
                        "triage_score": cached_patient.triage_score
                    }
                    patients.append(patient_record)
                
        return {"patients": sorted(patients, key=lambda x: x['triage_score']['score'], reverse=True)}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/tools/triage/{patient_id}", tags=["Triage"])
async def get_patient_by_id(patient_id: str) -> dict:
    try:
        load_env_file("dev.env")
        caching_manager = RedisManager()
        keys = caching_manager.get_keys(f"tools-triage-*-{patient_id}")
        
        if not keys:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Assume the latest entry is the one we want if there are multiple
        key = keys[-1]
        cached_patient_json = caching_manager.get_json(key)
        cached_patient = TriageInteractionRequest(**cached_patient_json)
        patient_record = {
            "request_id": cached_patient.request_id,
            "patient_id": cached_patient.patient_id,
            "params": cached_patient.params,
            "triage_score": cached_patient.triage_score
        }

        return {"patient": patient_record}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
