import uvicorn
from fastapi import FastAPI, Request, HTTPException
from caching.CacheRedis import RedisManager
from services.models.Models import FinalAssetInteractionRequest1
from services.service_mission_final_care_facilities.algos.pyreason.algo_mission_final_cfs_basic.AlgoFinalCF_Interaction import (
    FinalCFInteraction,
)
from utils.Utils import load_env_file

app = FastAPI()


@app.post("/tools/final_cf", tags=["FinalCF"])
async def final_cf_response(
    request: Request, interaction_request: FinalAssetInteractionRequest1
) -> FinalAssetInteractionRequest1:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-final-cf-{interaction_request.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_request_json = caching_manager.get_json(key)
        if cached_request_json is None:
            caching_manager.save_json(key, interaction_request.json())
        else:
            cached_request = FinalAssetInteractionRequest1(**cached_request_json)
            if cached_request.complete:
                return cached_request

        # Step 3. Interaction request
        print(f"Received request: {interaction_request}")  # Debug statement
        interaction_response = FinalCFInteraction().run_final_cf_algo(
            interaction_request=interaction_request
        )
        caching_manager.save_json(key, interaction_response.json())

        return interaction_response

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
