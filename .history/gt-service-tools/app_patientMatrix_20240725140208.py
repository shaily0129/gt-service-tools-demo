import uvicorn
from fastapi import FastAPI, Request, HTTPException
from caching.CacheRedis import RedisManager
from services.models.Models import PatientMatrixInteractionRequest
from services.service_patient_priority_matrix.algos.pyreason.algo_patient_matrix_basic.AlgoPatientMatrixInteraction import PatientMatrixInteraction
from utils.Utils import load_env_file

app = FastAPI()

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
    uvicorn.run(app, host="0.0.0.0", port=8003)
