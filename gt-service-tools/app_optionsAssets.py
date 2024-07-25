import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from caching.CacheRedis import RedisManager
from services.models.Models import InteractionRequest
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.service_mission_options_assets.algos.pyreason.algo_mission_options_assets_basic.AlgoOptionsAssetsInteraction import (
    OptionsAssetsInteraction,
)
from utils.Utils import load_env_file

app = FastAPI()


class MissionOptionsAssetsInteractionRequest(BaseModel):
    request_id: str
    params: List[Dict]
    interactions: Optional[List] = None
    complete: Optional[bool] = False
    final_asset: Optional[List[MissionOptionsAssets]] = None


@app.post("/tools/options_assets", tags=["OptionsAssets"])
async def options_assets_response(
    request: Request, interaction_request: MissionOptionsAssetsInteractionRequest
) -> MissionOptionsAssetsInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-options-assets-{interaction_request.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_request_json = caching_manager.get_json(key)
        if cached_request_json is None:
            caching_manager.save_json(key, interaction_request.json())
        else:
            cached_request = MissionOptionsAssetsInteractionRequest(
                **cached_request_json
            )
            if cached_request.complete:
                return cached_request

        # Step 3. Interaction request
        interaction_response = OptionsAssetsInteraction().run_options_assets_algo(
            interaction_request=interaction_request
        )
        caching_manager.save_json(key, interaction_response.json())

        return interaction_response

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
