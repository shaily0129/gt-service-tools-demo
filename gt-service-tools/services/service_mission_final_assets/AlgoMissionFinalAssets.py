from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets

class FinalAssets:
    def return_mission_final_asset(self, missions_options: list[MissionOptionsAssets])\
            -> list[MissionFinalAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")