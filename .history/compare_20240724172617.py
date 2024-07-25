from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryInteraction import TriageCategoryBasic
from services.models.Models import TriageInteractionRequest
from caching.CacheRedis import RedisManager
from utils.Utils import load_env_file

# Initialize caching manager
load_env_file("dev.env")
caching_manager = RedisManager()

# Step1 - Define initial parameters
name = "demo1"

# Step 2 - Create BookingInteractionRequest object
KEY = f"triage-category-{name.lower().replace(' ', '-')}"

# Step 3 - Save initial booking request if not already saved
if caching_manager.get_json(KEY) is None:
    #parameters = {'name': name, 'age': age, 'country': country}
    parameters = {}

    triage_interaction_request = TriageInteractionRequest(request_id=KEY, params=parameters)
    caching_manager.save_json(KEY, triage_interaction_request.json())

# Step 4 - Retrieve booking request from cache
triage_interaction_request_json = caching_manager.get_json(KEY)
bir = TriageInteractionRequest(**triage_interaction_request_json)

# Step 5 - Answer questions until booking is complete
if not bir.complete:
    bir = TriageCategoryBasic().run_triage_algo(triage_interaction_request=bir)
    if bir.interactions:
        for interaction in bir.interactions:
            interaction.answer = input(interaction.question)
            if interaction.answer is not None:
                bir.params[interaction.variable_name] = interaction.answer
                interaction.complete = True

        caching_manager.save_json(KEY, bir.json())
        print("More Q&A Needed, round we go again!")

# Step 6 - Display booking ID if booking is complete
if bir.complete:
    print(f"Triage category for patient id {bir.patient_id} is {bir.triage_category.category}")

print("Completed")