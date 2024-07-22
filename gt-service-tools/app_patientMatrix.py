import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
from caching.CacheRedis import RedisManager
from services.models.Models import PatientMatrixInteractionRequest
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoPatientMatrixInteraction import (
    PatientMatrixInteraction,
)
from services.models.ModelPatient import Patient
from utils.Utils import load_env_file
from utils.app_utils import app
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/tools/patient_matrix", tags=["Patient Matrix"])
async def calculate_patient_matrix(
    request: Request, matrix: PatientMatrixInteractionRequest
) -> PatientMatrixInteractionRequest:
    try:

        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-patient-matrix-{matrix.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_bir_json = caching_manager.get_json(key)
        if cached_bir_json is None:
            caching_manager.save_json(key, matrix.json())
        else:
            cached_bir = PatientMatrixInteractionRequest(**cached_bir_json)
            if cached_bir.complete:
                return cached_bir

        # Step 3. Interaction request
        bir = PatientMatrixInteraction().run_patient_matrix_algo(
            interaction_request=matrix
        )
        caching_manager.save_json(key, bir.json())

        logger.info("Response: %s", bir.json())
        return bir

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
