from services.service_mission_final_assets.AlgoMissionFinalAssets import FinalAssets
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from datetime import datetime
from typing import List, Dict
import networkx as nx
import pyreason as pr
import os
from mip import Model, xsum, maximize, BINARY


class AlgoMissionFinalAssetsInteraction(FinalAssets):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def use_milp(self, dict_triage_score: dict, dict_possible_assets: dict) -> dict:
        # [Use MILP logic here as in your provided code]
        pass

    def get_pyreason_bool(self, python_bool: bool) -> str:
        return "1,1" if python_bool else "0,0"

    def create_pyreason_graph(self, missions_options: List[MissionOptionsAssets]):
        g = nx.DiGraph()
        unique_assets = set()
        for mission in missions_options:
            patient_name = mission.patient_name
            triage_score = mission.triage_score
            possible_assets = mission.assets_possible
            g.add_node(patient_name, type_patient="1,1")
            g.add_edge(patient_name, str(triage_score), triage_score="1,1")
            unique_assets.update(possible_assets)

        for asset in unique_assets:
            g.add_node(asset, type_asset="1,1")

        for mission in missions_options:
            patient_name = mission.patient_name
            possible_assets = mission.assets_possible
            for asset in possible_assets:
                g.add_edge(patient_name, asset, possible_asset="1,1", final_asset="0,1")

        return g

    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_final_asset(
        self, missions_options: List[MissionOptionsAssets]
    ) -> List[MissionFinalAssets]:
        # [Logic to return final mission assets as in your provided code]
        pass

    def run_mission_final_asset_algo(self, mission_interaction_request):
        parameters = mission_interaction_request.params

        # Create MissionOptionsAssets objects
        missions_options = [MissionOptionsAssets(**param) for param in parameters]

        # Calculate Mission Final Assets
        mission_final_assets = self.return_mission_final_asset(missions_options)

        # Update the request with the results
        mission_interaction_request.mission_final_assets = mission_final_assets
        mission_interaction_request.complete = True

        # Cache result
        caching_manager = RedisManager()
        key = f"tools-mission-final-{mission_interaction_request.request_id}"
        caching_manager.save_json(key, mission_interaction_request.json())

        return mission_interaction_request
