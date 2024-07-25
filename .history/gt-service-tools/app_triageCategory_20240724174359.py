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
from fastapi import FastAPI, Request, HTTPException, Body
import uvicorn
from pydantic import BaseModel
from typing import Dict, Optional

from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryInteraction import TriageCategoryBasic
from services.models.Models import TriageInteractionRequest
from caching.CacheRedis import RedisManager
from utils.Utils import load_env_file

app = FastAPI()

# Initialize caching manager
load_env_file("dev.env")
caching_manager = RedisManager()

class TriageRequest(BaseModel):
    request_id: str
    params: Optional[Dict[str, str]] = None

@app.post("/tools/triage_category", tags=["Triage"])
async def triage_category(request: Request, triage: TriageRequest) -> Dict:
    try:
        # Define initial parameters
        KEY = f"triage-category-{triage.request_id.lower().replace(' ', '-')}"

        # Check for existing request in cache
        triage_interaction_request_json = caching_manager.get_json(KEY)
        if triage_interaction_request_json is None:
            # If not cached, save initial request
            parameters = triage.params or {}
            triage_interaction_request = TriageInteractionRequest(request_id=KEY, params=parameters)
            caching_manager.save_json(KEY, triage_interaction_request.json())
        else:
            triage_interaction_request = TriageInteractionRequest(**triage_interaction_request_json)

        # Answer questions until triage is complete
        if not triage_interaction_request.complete:
            triage_interaction_request = TriageCategoryBasic().run_triage_algo(triage_interaction_request=triage_interaction_request)
            if triage_interaction_request.interactions:
                for interaction in triage_interaction_request.interactions:
                    interaction.answer = input(interaction.question)
                    if interaction.answer is not None:
                        triage_interaction_request.params[interaction.variable_name] = interaction.answer
                        interaction.complete = True

                caching_manager.save_json(KEY, triage_interaction_request.json())
                return {"status": "More Q&A Needed, round we go again!"}

        # If triage is complete
        if triage_interaction_request.complete:
            return {"message": f"Triage category for patient id {triage_interaction_request.patient_id} is {triage_interaction_request.triage_category.category}"}

        return {"message": "Completed"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
