import uvicorn
from fastapi import FastAPI, HTTPException, Body, Request
from typing import Any, Dict, List
from pydantic import BaseModel
import logging
from caching.CacheRedis import RedisManager
from services.service_mission_final_assets.factory.FactoryAlgo import (
    MissionoptionsAssetsToMissionfinalAssetsFactory,
    MissionoptionsAssetsToMissionfinalAssetsAlgoName,
)
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoMissionFinalAssetsInteraction import (
    AlgoMissionFinalAssetsInteraction,
)
from services.models.Models import MissionInteractionRequest
from utils.Utils import load_env_file


class MissionFinalAssetResponse(BaseModel):
    request_id: str
    params: List[Dict[str, Any]]
    mission_final_assets: List[MissionFinalAssets]
    complete: bool


app = FastAPI(
    title="Mission Final Assets",
    description="API to determine the final asset allocation for missions",
    version="0.0.1",
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/tools/final-asset", tags=["asset"])
async def rate_response(
    request: Request, body: MissionInteractionRequest = Body(...)
) -> MissionInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-mission-final-{body.request_id}"

        # Create TriageInteractionRequest from request body
        mission_interaction_request = MissionInteractionRequest(
            request_id=body.request_id, params=body.params
        )

        # Step 2. Check for new or complete interaction request
        cached_mir_json = caching_manager.get_json(key)
        if cached_mir_json is None:
            caching_manager.save_json(key, mission_interaction_request.json())
        else:
            cached_mir = MissionInteractionRequest(**cached_mir_json)
            if cached_mir.complete:
                return cached_mir

        # Step 3. Interaction request
        mission_algo = AlgoMissionFinalAssetsInteraction()
        mission_interaction_request = mission_algo.run_mission_final_asset_algo(
            mission_interaction_request=mission_interaction_request
        )

        # Step 4. Save the result and return it
        caching_manager.save_json(key, mission_interaction_request.json())
        return mission_interaction_request

    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
