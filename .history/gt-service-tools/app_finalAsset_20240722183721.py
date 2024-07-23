import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
from typing import List, Dict
from caching.CacheRedis import RedisManager
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoMissionFinalAssetsInteraction import (
    MissionFinalAssetsInteraction,
)
from utils.Utils import load_env_file


class MissionRequestBody(BaseModel):
    request_id: str
    params: Dict


app = FastAPI(
    title="Mission Final Assets",
    description="Web-enabled version of mission final assets assignment",
    version="0.0.1",
)


@app.post("/tools/mission_final_assets", tags=["Mission Final Assets"])
async def mission_final_assets(
    request: Request, body: MissionRequestBody = Body(...)
) -> List[MissionFinalAssets]:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-mission-final-assets-{body.request_id}"

        # Check for new or complete interaction request
        cached_mission_json = caching_manager.get_json(key)
        if cached_mission_json is None:
            caching_manager.save_json(key, body.params)
        else:
            cached_mission = [
                MissionFinalAssets(**item) for item in cached_mission_json
            ]
            if cached_mission is not None:
                return cached_mission

        # Create MissionOptionsAssets from request body params
        mission_options = MissionOptionsAssets(**body.params)

        # Run the mission final assets algorithm with interaction
        interaction = MissionFinalAssetsInteraction()
        final_assets = interaction.run_mission_final_assets_algo(
            mission_interaction_request=mission_options
        )

        # Save the result and return it
        caching_manager.save_json(key, [asset.dict() for asset in final_assets])
        return final_assets

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
