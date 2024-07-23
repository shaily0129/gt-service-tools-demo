from services.models.Models import MissionFinalAssetsRequest
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.service_mission_final_assets.factory.FactoryAlgo import (
    MissionoptionsAssetsToMissionfinalAssetsFactory,
    MissionoptionsAssetsToMissionfinalAssetsAlgoName,
)
from caching.CacheRedis import RedisManager


class MissionFinalAssetsInteraction:
    def __init__(self):
        pass

    def run_mission_final_assets_algo(
        self, interaction_request: MissionFinalAssetsRequest
    ) -> MissionFinalAssetsRequest:
        parameters = interaction_request.params

        # Create MissionOptionsAssets objects
        missions = [
            MissionOptionsAssets(**params) for params in parameters.get("missions", [])
        ]

        # Calculate Mission Final Assets
        algo_mission_assets = MissionoptionsAssetsToMissionfinalAssetsFactory.create_missionoptionsAssets_to_missionfinalAssets_algo(
            mode=MissionoptionsAssetsToMissionfinalAssetsAlgoName.BASIC
        )
        assets_all_missions = algo_mission_assets.return_mission_final_asset(
            missions_options=missions
        )
        interaction_request.missions = assets_all_missions
        interaction_request.complete = True

        # Cache result
        caching_manager = RedisManager()
        key = f"tools-mission-final-assets-{interaction_request.request_id}"
        caching_manager.save_json(key, interaction_request.json())

        return interaction_request
