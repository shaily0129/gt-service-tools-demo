import os
from datetime import datetime
from typing import List

from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsBasic import (
    MissionFinalAssetsBasic,
)
from services.models.Models import FinalAssetInteractionRequest, MissionFinalAssets
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
import pyreason as pr


class FinalAssetInteraction(MissionFinalAssetsBasic):

    def __init__(self):
        super().__init__()

    def run_final_asset_algo(
        self, asset_interaction_request: FinalAssetInteractionRequest
    ) -> FinalAssetInteractionRequest:
        parameters = asset_interaction_request.params
        missions_options = [MissionOptionsAssets(**params) for params in parameters]

        # Calculate Final Assets
        mission_final_assets = self.return_mission_final_asset(missions_options)

        asset_interaction_request.final_asset = mission_final_assets
        asset_interaction_request.complete = True
        asset_interaction_request.interactions = None

        return asset_interaction_request

    def return_mission_final_asset(
        self, missions_options: List[MissionOptionsAssets]
    ) -> List[MissionFinalAssets]:
        mission_final_assets = []

        # Set pyreason settings
        graph = self.create_pyreason_graph(missions_options)
        graphml_path = "pyreason_input_graph_mission_options_assets.graphml"
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = "rules_mission_options_assets_to_final_assets.txt"
        self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
        rules_path = os.path.join(current_script_directory, rules_path)

                pr.reset()
        pr.reset_rules()
        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True

        pr.load_graphml(graphml_path)
        pr.add_rules_from_file(rules_path, infer_edges=False)

        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1
        folder_name = "traces_t0_mission_options_assets_to_final_assets"
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        patients_list = []
        field = "trigger_optimization"
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        p_name = df["component"][i]
                        patients_list.append(p_name)

        dict_patients_triage_score = {}
        field = "triage_score"
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        p_name = df["component"][i][0]
                        triage_score = float(df["component"][i][1])
                        triage_score = triage_score / 100
                        if p_name in patients_list:
                            dict_patients_triage_score[p_name] = triage_score

        dict_patients_possible_assets = {}
        for p in patients_list:
            dict_patients_possible_assets[p] = []

        field = "possible_asset"
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        p_name = df["component"][i][0]
                        a_name = df["component"][i][1]
                        if p_name in patients_list:
                            dict_patients_possible_assets[p_name].append(a_name)

        selected_persons, assigned_resources = self.use_milp(
            dict_triage_score=dict_patients_triage_score,
            dict_possible_assets=dict_patients_possible_assets,
        )

        edge_facts = []
        for index, assigned_person_resource in enumerate(assigned_resources):
            fact_mlp_result = pr.fact_edge.Fact(
                f"f_mlp_result_{index}",
                (assigned_person_resource[1], assigned_person_resource[0]),
                pr.label.Label("mlp_optimized"),
                pr.interval.closed(1, 1),
                self.next_time,
                self.next_time,
            )
            edge_facts.append(fact_mlp_result)

        self.interpretation = pr.reason(again=True, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = "traces_t1_mission_options_assets_to_final_assets"
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        dict_patients_final_asset = {}
        field = "final_asset"
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        p_name = df["component"][i][0]
                        a_name = df["component"][i][1]
                        dict_patients_final_asset[p_name] = a_name

        for patient in patients_list:
            if patient not in dict_patients_final_asset:
                dict_patients_final_asset[patient] = "NA"

        for key, value in dict_patients_final_asset.items():
            mission_final_assets.append(
                MissionFinalAssets(
                    patient_name=key,
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name="pyreason_basic",
                    asset_final=value,
                    asset_details=None,
                    confidence=1.0,
                    rationale=None,
                    interaction=None,
                )
            )

        return mission_final_assets
