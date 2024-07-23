# import uvicorn
# from caching.CacheRedis import RedisManager
# from fastapi import FastAPI, Request, HTTPException
# from services.models.Models import FinalAssetInteractionRequest
# from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoFinalAssetInteraction import (
#     FinalAssetInteraction,
# )
# from utils.Utils import load_env_file

# app = FastAPI()


# @app.post("/tools/final_asset", tags=["asset"])
# async def rate_response(
#     request: Request, asset: FinalAssetInteractionRequest
# ) -> FinalAssetInteractionRequest:
#     try:
#         # Step 1. Setup Caching Manager
#         load_env_file("dev.env")
#         caching_manager = RedisManager()
#         key = f"tools-asset-{asset.request_id}"

#         # Step 2. Check for new or complete interaction request
#         cached_asset_json = caching_manager.get_json(key)
#         if cached_asset_json is None:
#             caching_manager.save_json(key, asset.json())
#         else:
#             cached_asset = FinalAssetInteractionRequest(**cached_asset_json)
#             if cached_asset.complete:
#                 return cached_asset

#         # Step 3. Interaction request
#         final_asset_interaction = FinalAssetInteraction()
#         asset = final_asset_interaction.run_final_asset_algo(
#             asset_interaction_request=asset
#         )
#         caching_manager.save_json(key, asset.json())

#         return asset

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8002)


import uvicorn
from fastapi import FastAPI, Request, HTTPException
from caching.CacheRedis import RedisManager
from services.models.Models import FinalAssetInteractionRequest
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoFinalAssetInteraction import (
    FinalAssetInteraction,
)
from utils.Utils import load_env_file

app = FastAPI()


@app.post("/tools/final_asset", tags=["asset"])
async def rate_response(
    request: Request, asset: FinalAssetInteractionRequest
) -> FinalAssetInteractionRequest:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-asset-{asset.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_asset_json = caching_manager.get_json(key)
        if cached_asset_json is None:
            caching_manager.save_json(key, asset.json())
        else:
            cached_asset = FinalAssetInteractionRequest(**cached_asset_json)
            if cached_asset.complete:
                return cached_asset

        # Step 3. Interaction request
        final_asset_interaction = FinalAssetInteraction()
        asset = final_asset_interaction.run_final_asset_algo(
            asset_interaction_request=asset
        )
        caching_manager.save_json(key, asset.json())

        return asset

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
