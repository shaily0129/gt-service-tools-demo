
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsBasic import MissionFinalAssetsBasic
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class MissionoptionsAssetsToMissionfinalAssetsAlgoName(Enum):
    BASIC = "basic"

class MissionoptionsAssetsToMissionfinalAssetsFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_missionoptionsAssets_to_missionfinalAssets_algo(mode:str):
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.BASIC:
            return MissionFinalAssetsBasic()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")