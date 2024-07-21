# from services.models.ModelPatient import Patient
from services.models.ModelAsset import Asset
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets

class OptionsAssets:
    def return_mission_options_assets(self, mission_requirements: list[MissionRequirements], assets: list[Asset])\
            -> list[MissionOptionsAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")