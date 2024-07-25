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
from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryInteraction import (
    TriageCategoryBasic,
)
from services.models.Models import TriageInteractionRequest
from caching.CacheRedis import RedisManager
from utils.Utils import load_env_file
import json

app = FastAPI()

# Initialize caching manager
load_env_file("dev.env")
caching_manager = RedisManager()


class InteractionResponse(BaseModel):
    request_id: str
    question: str
    variable_name: str


class InteractionAnswer(BaseModel):
    request_id: str
    variable_name: str
    answer: str


@app.post("/start_triage_interaction/")
async def start_triage_interaction(request: Request):
    data = await request.json()
    name = data.get("name", "demo1")
    KEY = f"triage-category-{name.lower().replace(' ', '-')}"

    if caching_manager.get_json(KEY) is None:
        parameters = {}
        triage_interaction_request = TriageInteractionRequest(
            request_id=KEY, params=parameters
        )
        caching_manager.save_json(KEY, triage_interaction_request.json())

    triage_interaction_request_json = caching_manager.get_json(KEY)
    bir = TriageInteractionRequest(**triage_interaction_request_json)

    if not bir.complete:
        bir = TriageCategoryBasic().run_triage_algo(triage_interaction_request=bir)
        if bir.interactions:
            interaction = bir.interactions[0]  # Get the first unanswered question
            caching_manager.save_json(KEY, bir.json())
            return InteractionResponse(
                request_id=bir.request_id,
                question=interaction.question,
                variable_name=interaction.variable_name,
            )
        else:
            caching_manager.save_json(KEY, bir.json())

    if bir.complete:
        return {
            "message": f"Triage category for patient id {bir.patient_id} is {bir.triage_category.category}"
        }

    return {"message": "More Q&A Needed, round we go again!"}


@app.post("/answer_interaction/")
async def answer_interaction(answer: InteractionAnswer):
    KEY = answer.request_id
    triage_interaction_request_json = caching_manager.get_json(KEY)
    if not triage_interaction_request_json:
        raise HTTPException(status_code=404, detail="Request ID not found")

    bir = TriageInteractionRequest(**triage_interaction_request_json)
    if not bir.complete:
        for interaction in bir.interactions:
            if interaction.variable_name == answer.variable_name:
                interaction.answer = answer.answer
                bir.params[interaction.variable_name] = interaction.answer
                interaction.complete = True
                break

        bir = TriageCategoryBasic().run_triage_algo(triage_interaction_request=bir)
        caching_manager.save_json(KEY, bir.json())

    if bir.complete:
        return {
            "message": f"Triage category for patient id {bir.patient_id} is {bir.triage_category.category}"
        }

    next_interaction = next((i for i in bir.interactions if not i.complete), None)
    if next_interaction:
        return InteractionResponse(
            request_id=bir.request_id,
            question=next_interaction.question,
            variable_name=next_interaction.variable_name,
        )

    return {"message": "More Q&A Needed, round we go again!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
