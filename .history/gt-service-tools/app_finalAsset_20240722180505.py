import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.Models import MissionFinalAssetsRequest
from services.service_mission_final_assets.factory.FactoryAlgo import MissionoptionsAssetsToMissionfinalAssetsFactory, MissionoptionsAssetsToMissionfinalAssetsAlgoName
from caching.CacheRedis import RedisManager
from utils.Utils import load_env_file

app = FastAPI()

@app.post("/tools/mission_final_assets", tags=["Mission Final Assets"])
async def calculate_mission_final_assets(
    request: Request, mission_request: MissionFinalAssetsRequest
) -> MissionFinalAssetsRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-mission-final-assets-{mission_request.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_request_json = caching_manager.get_json(key)
        if cached_request_json is None:
            caching_manager.save_json(key, mission_request.json())
        else:
            cached_request = MissionFinalAssetsRequest(**cached_request_json)
            if cached_request.complete:
                return cached_request

        # Step 3. Interaction request
        missions = mission_request.missions or []
        algo_mission_assets = MissionoptionsAssetsToMissionfinalAssetsFactory.create_missionoptionsAssets_to_missionfinalAssets_algo(
            mode=MissionoptionsAssetsToMissionfinalAssetsAlgoName.BASIC
        )
        assets_all_missions = algo_mission_assets.return_mission_final_asset(missions_options=missions)
        mission_request.missions = assets_all_missions
        mission_request.complete = True

        caching_manager.save_json(key, mission_request.json())

        return mission_request

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
