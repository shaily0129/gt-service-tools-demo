# from http.client import HTTPException
# import uvicorn
# from caching.CacheRedis import RedisManager

# from services.models.Models import TriageInteractionRequest1

# from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryInteraction import (
#     TriageCategoryBasic,
# )
# from utils.app_utils import app
# from fastapi import Request, HTTPException
# from utils.Utils import load_env_file


# @app.post("/tools/triage_category", tags=["Triage"])
# async def rate_response(
#     request: Request, triage: TriageInteractionRequest1
# ) -> TriageInteractionRequest1:
#     try:
#         # Step 1. Setup Caching Manager
#         load_env_file("dev.env")
#         caching_manager = RedisManager()
#         key = f"tools-triage-{triage.request_id}"

#         # Step 2. Check for new or complete interaction request
#         cached_bir_json = caching_manager.get_json(key)
#         if cached_bir_json is None:
#             caching_manager.save_json(key, triage.json())
#         else:
#             cached_bir = TriageInteractionRequest1(**cached_bir_json)
#             if cached_bir.complete:
#                 return cached_bir

#         # Step 3. Interaction request
#         bir = TriageCategoryBasic().run_triage_algo(triage_interaction_request=triage)
#         caching_manager.save_json(key, bir.json())

#         return bir

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8002)


from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
from typing import Optional
from caching.CacheRedis import RedisManager
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryInteraction import (
    TriageCategoryBasic,
)
from utils.Utils import load_env_file

app = FastAPI()


class TriageInteractionRequest(BaseModel):
    request_id: str
    patient_id: str
    triage_score: int
    complete: Optional[bool] = False
    interactions: Optional[list] = []


class TriageCategoryResponse(BaseModel):
    patient_name: str
    datetime_seconds: int
    algo_name: str
    category: str
    confidence: float
    rationale: Optional[str] = None
    interaction: Optional[str] = None


@app.post(
    "/tools/triage_category", response_model=TriageCategoryResponse, tags=["Triage"]
)
async def rate_response(triage: TriageInteractionRequest) -> TriageCategoryResponse:
    try:
        # Step 1. Setup Caching Manager
        load_env_file("dev.env")
        caching_manager = RedisManager()
        key = f"tools-triage-{triage.request_id}"

        # Step 2. Check for new or complete interaction request
        cached_bir_json = caching_manager.get_json(key)
        if cached_bir_json is None:
            caching_manager.save_json(key, triage.json())
        else:
            cached_bir = TriageInteractionRequest(**cached_bir_json)
            if cached_bir.complete:
                return cached_bir

        # Step 3. Interaction request
        bir = TriageCategoryBasic().run_triage_algo(triage_interaction_request=triage)
        caching_manager.save_json(key, bir.json())

        triage_category_response = TriageCategoryResponse(
            patient_name=bir.patient_name,
            datetime_seconds=bir.datetime_seconds,
            algo_name=bir.algo_name,
            category=bir.triage_category.category,
            confidence=bir.triage_category.confidence,
            rationale=bir.triage_category.rationale,
            interaction=bir.triage_category.interaction,
        )

        return triage_category_response

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
