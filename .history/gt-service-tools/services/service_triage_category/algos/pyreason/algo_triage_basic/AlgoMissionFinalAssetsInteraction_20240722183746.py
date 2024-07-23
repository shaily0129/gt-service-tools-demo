from typing import List, Dict, Optional
from services.service_mission_final_assets.AlgoMissionFinalAssets import FinalAssets
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsBasic import (
    MissionFinalAssetsBasic,
)
from datetime import datetime


class MissionFinalAssetsInteraction(FinalAssets):

    def __init__(self):
        self.thresholds = None

    def validate_assets(self, assets: List[str]):
        valid_assets = [
            "Black hawk HH60M",
            "Chinook CH47",
            "Chinook CH99",
            "Truck M1165",
            "Ambulance M997A3",
        ]
        for asset in assets:
            if asset not in valid_assets:
                raise ValueError(f"{asset} is not a valid asset")

    def validate_mission_options(self, mission_options: List[MissionOptionsAssets]):
        for mission in mission_options:
            self.validate_assets(mission.assets_possible)

    def run_mission_final_assets_algo(
        self, mission_interaction_request: MissionOptionsAssets
    ) -> List[MissionFinalAssets]:
        mission_options = [mission_interaction_request]

        # Validate the mission options
        self.validate_mission_options(mission_options)

        # Initialize the algorithm
        algo_mission_assets = MissionFinalAssetsBasic()

        # Calculate final assets
        final_assets = algo_mission_assets.return_mission_final_asset(
            missions_options=mission_options
        )

        return final_assets

    def missing_values(self, params: Dict) -> Optional[List[str]]:
        required_fields = ["patient_name", "assets_possible", "triage_score"]
        missing_fields = [field for field in required_fields if field not in params]
        return missing_fields if missing_fields else None
