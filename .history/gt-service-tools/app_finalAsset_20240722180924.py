import uvicorn
from fastapi import FastAPI, HTTPException, Request
from services.models.Models import MissionFinalAssetsRequest
from caching.CacheRedis import RedisManager
from utils.Utils import load_env_file
from finalAssetsInteraction import MissionFinalAssetsInteraction

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
        interaction = MissionFinalAssetsInteraction()
        mission_request = interaction.run_mission_final_assets_algo(mission_request)
        caching_manager.save_json(key, mission_request.json())

        return mission_request

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
