from caching.CacheRedis import RedisManager
import uvicorn
from fastapi import FastAPI, HTTPException, Body, Request
from typing import List
from pydantic import BaseModel
from services.service_mission_final_assets.factory.FactoryAlgo import (
    MissionoptionsAssetsToMissionfinalAssetsFactory,
    MissionoptionsAssetsToMissionfinalAssetsAlgoName,
)
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoMissionFinalAssetsInteraction import (
    AlgoMissionFinalAssetsInteraction,
)
from utils.Utils import load_env_file


class MissionInteractionRequest(BaseModel):
    request_id: str
    params: List[MissionOptionsAssets]
    mission_final_assets: List[MissionFinalAssets] = []
    complete: bool = False


class MissionFinalAssetResponse(BaseModel):
    request_id: str
    params: List[MissionOptionsAssets]
    mission_final_assets: List[MissionFinalAssets]
    complete: bool


app = FastAPI(
    title="Mission Final Assets",
    description="API to determine the final asset allocation for missions",
    version="0.0.1",
)


@app.post("/tools/final-asset", tags=["asset"])
async def rate_response(
    request: Request, body: MissionInteractionRequest = Body(...)
) -> MissionInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-triage-{body.request_id}"

        # Create TriageInteractionRequest from request body
        triage_interaction_request = MissionInteractionRequest(
            request_id=body.request_id, params=body.params
        )

        # Step 2. Check for new or complete interaction request
        cached_bir_json = caching_manager.get_json(key)
        if cached_bir_json is None:
            caching_manager.save_json(key, triage_interaction_request.json())
        else:
            cached_bir = MissionInteractionRequest(**cached_bir_json)
            if cached_bir.complete:
                return cached_bir

        # Step 3. Interaction request is still WIP, so run the triage algorithm and cache result
        bir = AlgoMissionFinalAssetsInteraction().run_mission_final_asset_algo(
            mission_interaction_request=body
        )

        # Step 4. Save the result and return it
        caching_manager.save_json(key, bir.json())
        return bir

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
