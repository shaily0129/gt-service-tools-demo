from typing import List, Union
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


# class TriageRequestBody(BaseModel):
#     request_id: str
#     params: dict

class PatientParams(BaseModel):
    patient_id: str  # Mandatory field
    params: dict

class TriageRequestBody(BaseModel):
    request_id: str
    patients: Union[PatientParams, List[PatientParams]]  # Can be a single patient or a list of patients

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
) -> TriageInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-triage-{body.request_id}"

        # Create TriageInteractionRequest from request body
        triage_interaction_request = TriageInteractionRequest(
            request_id=body.request_id, params=body.params
        )

        # Step 2. Check for new or complete interaction request
        cached_bir_json = caching_manager.get_json(key)
        if cached_bir_json is None:
            caching_manager.save_json(key, triage_interaction_request.json())
        else:
            cached_bir = TriageInteractionRequest(**cached_bir_json)
            if cached_bir.complete:
                return cached_bir

        # Step 3. Interaction request is still WIP, so run the triage algorithm and cache result
        bir = TriageScoreInteraction(thresholds=thresholds_data_algo3).run_triage_algo(
            triage_interaction_request=triage_interaction_request
        )

        # Step 4. Save the result and return it
        caching_manager.save_json(key, bir.json())
        return bir

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
