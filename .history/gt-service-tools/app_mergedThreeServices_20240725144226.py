import json
from typing import Dict, List
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
from caching.CacheRedis import RedisManager
from services.models.Models import (
    FinalAssetInteractionRequest,
    TriageInteractionRequest,
    TriageInteractionRequest1,
    PatientMatrixInteractionRequest,
)
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoFinalAssetInteraction import (
    FinalAssetInteraction,
)
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageScoreInteraction import (
    TriageScoreInteraction,
)
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryInteraction import (
    TriageCategoryBasic,
)
from services.service_patient_priority_matrix.algos.pyreason.algo_patient_matrix_basic.AlgoPatientMatrixInteraction import (
    PatientMatrixInteraction,
)
from services.service_triage.factory.FactoryAlgoTriage import (
    Threshold,
)
from utils.Utils import load_env_file
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ASU Tools",
    description="Demo of using interactive tools",
    version="0.0.1",
)


class PatientParams(BaseModel):
    patient_id: str  # Mandatory field
    params: dict


class TriageRequestBody(BaseModel):
    request_id: str
    patients: List[PatientParams]


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


@app.post("/tools/final_asset", tags=["asset"])
async def rate_response(
    request: Request, asset: FinalAssetInteractionRequest
) -> FinalAssetInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-asset-{asset.request_id}"

        # Clear cache before processing the request
        caching_manager.delete(key)

        # Step 2. Check for new or complete interaction request
        cached_asset_json = caching_manager.get_json(key)
        if cached_asset_json is None:
            caching_manager.save_json(key, asset.json())
        else:
            cached_asset = FinalAssetInteractionRequest(**cached_asset_json)
            if cached_asset.complete:
                return cached_asset

        # Step 3. Interaction request
        final_asset_interaction = FinalAssetInteraction()
        asset = final_asset_interaction.run_final_asset_algo(
            asset_interaction_request=asset
        )
        caching_manager.save_json(key, asset.json())

        return asset

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/triage", tags=["Triage"])
async def rate_response(request: Request, body: TriageRequestBody = Body(...)) -> dict:
    try:
        load_env_file("dev.env")
        caching_manager = RedisManager()

        results = []
        for patient in body.patients:
            key = f"tools-triage-{body.request_id}-{patient.patient_id}"
            triage_interaction_request = TriageInteractionRequest(
                request_id=body.request_id,
                patient_id=patient.patient_id,
                params=patient.params,
            )

            cached_bir_json = caching_manager.get_json(key)
            if cached_bir_json is None:
                caching_manager.save_json(key, triage_interaction_request.json())
            else:
                cached_bir = TriageInteractionRequest(**cached_bir_json)
                if cached_bir.complete:
                    results.append(cached_bir)
                    continue

            bir = TriageScoreInteraction(
                thresholds=thresholds_data_algo3
            ).run_triage_algo(triage_interaction_request=triage_interaction_request)

            caching_manager.save_json(key, bir.json())
            results.append(bir)

        sorted_results = sorted(
            results, key=lambda x: x.triage_score.score, reverse=True
        )

        return {"results": sorted_results}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/triage/scores", tags=["Triage"])
async def get_patient_scores(
    request: Request, patient_ids: List[str] = Body(...)
) -> dict:
    try:
        load_env_file("dev.env")
        caching_manager = RedisManager()

        results = []
        for patient_id in patient_ids:
            keys = caching_manager.get_keys(f"tools-triage-*-{patient_id}")
            if not keys:
                continue

            key = keys[-1]
            cached_patient_json = caching_manager.get_json(key)

            cached_patient_dict = json.loads(cached_patient_json)
            cached_patient = TriageInteractionRequest(**cached_patient_dict)
            patient_record = {
                "patient_id": cached_patient.patient_id,
                "triage_score": cached_patient.triage_score,
                "algo_name": cached_patient.triage_score.algo_name,
            }
            results.append(patient_record)

        sorted_results = sorted(
            results, key=lambda x: x["triage_score"].score, reverse=True
        )

        return {"patients": sorted_results}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/triage_category", tags=["Triage"])
async def rate_response(
    request: Request, triage: TriageInteractionRequest1
) -> TriageInteractionRequest1:
    try:
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-triage-{triage.request_id}"

        cached_bir_json = caching_manager.get_json(key)
        if cached_bir_json is None:
            caching_manager.save_json(key, triage.json())
        else:
            cached_bir = TriageInteractionRequest1(**cached_bir_json)
            if cached_bir.complete:
                return cached_bir

        bir = TriageCategoryBasic().run_triage_algo(triage_interaction_request=triage)
        caching_manager.save_json(key, bir.json())

        return bir

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/patient_matrix", tags=["PatientMatrix"])
async def patient_matrix_response(
    request: Request, interaction_request: PatientMatrixInteractionRequest
) -> PatientMatrixInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-patient-matrix-{interaction_request.request_id or interaction_request.patient_id}"

        # Step 2. Check for new or complete interaction request
        cached_request_json = caching_manager.get_json(key)
        if cached_request_json is None:
            caching_manager.save_json(key, interaction_request.json())
        else:
            cached_request = PatientMatrixInteractionRequest(**cached_request_json)
            if cached_request.complete:
                return cached_request

        # Step 3. Interaction request
        print(f"Received request: {interaction_request}")  # Debug statement
        interaction_response = PatientMatrixInteraction().run_patient_matrix_algo(
            interaction_request=interaction_request
        )
        caching_manager.save_json(key, interaction_response.json())

        return interaction_response

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
