import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from caching.CacheRedis import RedisManager
from services.models.Models import MissionFinalAssetsRequest
from services.service_mission_final_assets.factory.FactoryAlgo import (
    MissionoptionsAssetsToMissionfinalAssetsFactory,
    MissionoptionsAssetsToMissionfinalAssetsAlgoName,
)
from services.service_mission_final_assets.AlgoMissionFinalAssets import FinalAssets
from utils.Utils import load_env_file
from utils.app_utils import app

@app.post("/tools/mission_final_assets", tags=["Mission Final Assets"])
async def calculate_mission_final_assets(
    request: Request, mission: MissionFinalAssetsRequest
) -> MissionFinalAssetsRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-mission-final-assets-{mission.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_mission_json = caching_manager.get_json(key)
        if cached_mission_json is None:
            caching_manager.save_json(key, mission.json())
        else:
            cached_mission = MissionFinalAssetsRequest(**cached_mission_json)
            if cached_mission.complete:
                return cached_mission

        # Step 3. Interaction request
        final_assets_interaction = MissionFinalAssetsInteraction().run_mission_final_assets_algo(
            interaction_request=mission
        )
        caching_manager.save_json(key, final_assets_interaction.json())

        return final_assets_interaction

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
