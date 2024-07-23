import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
from typing import List, Dict, Any
from caching.CacheRedis import RedisManager
from services.models.Models import MissionInteractionRequest
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoMissionFinalAssetsInteraction import (
    AlgoMissionFinalAssetsInteraction,
)
import traceback
from utils.Utils import load_env_file


class MissionRequestBody(BaseModel):
    request_id: str
    params: List[Dict[str, Any]]


app = FastAPI(
    title="ASU Tools",
    description="Demo of using interactive tools",
    version="0.0.1",
)


@app.post("/tools/mission-final-asset", tags=["Mission Final Asset"])
async def mission_final_asset_response(
    request: Request, assest: MissionRequestBody = Body(...)
) -> MissionInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-mission-final-{assest.request_id}"

        # Create MissionInteractionRequest from request body
        mission_interaction_request = MissionInteractionRequest(
            request_id=assest.request_id, params=asses=t.params
        )

        # Step 2. Check for new or complete interaction request
        cached_mission_json = caching_manager.get_json(key)
        if cached_mission_json is None:
            caching_manager.save_json(key, mission_interaction_request.json())
        else:
            cached_mission = MissionInteractionRequest(**cached_mission_json)
            if cached_mission.complete:
                return cached_mission

        # Step 3. Interaction request is still WIP, so run the mission final asset algorithm and cache result
        mission_algo = AlgoMissionFinalAssetsInteraction()
        mission_result = mission_algo.run_mission_final_asset_algo(
            mission_interaction_request=mission_interaction_request
        )

        # Step 4. Save the result and return it
        caching_manager.save_json(key, mission_result.json())
        return mission_result

    except Exception as e:
        error_message = str(e)
        print("Error occurred:", error_message)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_message)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
