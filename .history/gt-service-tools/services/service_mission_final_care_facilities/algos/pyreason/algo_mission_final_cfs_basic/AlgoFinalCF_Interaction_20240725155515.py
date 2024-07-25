from typing import Dict, List
from services.service_mission_final_care_facilities.AlgoMissionFinalCFs import (
    FinalCareFacilities,
)
from services.models.ModelMissionFinalCFs import MissionFinalCFs
from services.models.ModelMissionOptionsCFs import MissionOptionsCFs
from services.models.Models import FinalAssetInteractionRequest1, Interaction
from datetime import datetime
import networkx as nx
import pyreason as pr
import os
from mip import Model, xsum, maximize, BINARY


class FinalCFInteraction(FinalCareFacilities):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def use_milp(self, dict_triage_score: dict, dict_possible_cfs: dict) -> dict:
        persons = list(dict_triage_score.keys())
        w_p = {}
        resources_persons = []
        unique_cfs = set()
        for person, score in dict_triage_score.items():
            w_p[person] = 1 - score
        for person, possible_cfs in dict_possible_cfs.items():
            unique_cfs.update(possible_cfs)
            for cf in possible_cfs:
                resources_persons.append((cf, person))
        resources = list(unique_cfs)

        person_index = {person: i for i, person in enumerate(persons)}
        resource_index = {resource: i for i, resource in enumerate(resources)}

        m = Model("resource_person_assignment")

        X = {}
        for r, p in resources_persons:
            r_idx = resource_index[r]
            p_idx = person_index[p]
            X[(r_idx, p_idx)] = m.add_var(var_type=BINARY)

        Y = [m.add_var(var_type=BINARY) for _ in persons]

        m.objective = maximize(xsum(Y[person_index[p]] * w_p[p] for p in persons))

        for p in persons:
            p_idx = person_index[p]
            m += (
                xsum(X[(r_idx, p_idx)] for r_idx, p_idx2 in X.keys() if p_idx2 == p_idx)
                >= Y[p_idx]
            )

        for r in resources:
            r_idx = resource_index[r]
            m += (
                xsum(X[(r_idx, p_idx)] for r_idx2, p_idx in X.keys() if r_idx2 == r_idx)
                <= 1
            )

        m.optimize()

        selected_persons = [p for p in persons if Y[person_index[p]].x >= 0.99]
        assigned_resources = [
            (resources[r_idx], persons[p_idx])
            for (r_idx, p_idx) in X.keys()
            if X[(r_idx, p_idx)].x >= 0.99
        ]

        return selected_persons, assigned_resources

    def get_pyreason_bool(self, python_bool: bool) -> str:
        return "1,1" if python_bool else "0,0"

    def create_pyreason_graph(self, missions_options: list[MissionOptionsCFs]):
        g = nx.DiGraph()
        unique_cfs = set()
        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            triage_score = mission.triage_score
            possible_cfs = mission.care_facilities_possible
            g.add_node(patient_name, type_patient="1,1")
            g.add_edge(patient_name, str(triage_score), triage_score="1,1")

            unique_cfs.update(possible_cfs)

        for cf in unique_cfs:
            g.add_node(cf, type_cf="1,1")
        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            possible_cfs = mission.care_facilities_possible

            for i in range(len(possible_cfs)):
                g.add_edge(
                    patient_name, possible_cfs[i], possible_cf="1,1", final_cf="0,1"
                )

        return g

    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_final_care_facility(
        self, missions_options: list[MissionOptionsCFs]
    ) -> list[MissionFinalCFs]:
        mission_final_cfs = []
        graph = self.create_pyreason_graph(missions_options)
        graphml_path = "pyreason_input_graph_mission_options_cfs.graphml"
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = "rules_mission_options_cfs_to_final_cfs.txt"
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
        folder_name = "traces_t0_mission_options_cfs_to_final_cfs"
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
                        triage_score = float(df["component"][i][1]) / 100
                        if p_name in patients_list:
                            dict_patients_triage_score[p_name] = triage_score

        dict_patients_possible_cfs = {p: [] for p in patients_list}

        field = "possible_cf"
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        p_name = df["component"][i][0]
                        c_name = df["component"][i][1]
                        if p_name in patients_list:
                            dict_patients_possible_cfs[p_name].append(c_name)

        _, assigned_persons_resource = self.use_milp(
            dict_triage_score=dict_patients_triage_score,
            dict_possible_cfs=dict_patients_possible_cfs,
        )

        edge_facts = []
        for index, assigned_person_resource in enumerate(assigned_persons_resource):
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
        folder_name = "traces_t1_mission_options_cfs_to_final_cfs"
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        dict_patients_final_cf = {}
        field = "final_cf"
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        p_name = df["component"][i][0]
                        c_name = df["component"][i][1]
                        dict_patients_final_cf[p_name] = c_name
        for patient in patients_list:
            if patient not in dict_patients_final_cf:
                dict_patients_final_cf[patient] = "NA"
        for key, value in dict_patients_final_cf.items():
            mission_final_cfs.append(
                MissionFinalCFs(
                    patient_name=key,
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name="pyreason_basic",
                    cf_final=value,
                    cf_details=None,
                    confidence=1.0,
                    rationale=None,
                    interaction=None,
                )
            )

        return mission_final_cfs

    def run_final_cf_algo(
        self, interaction_request: FinalAssetInteractionRequest1
    ) -> FinalAssetInteractionRequest1:
        params = interaction_request.params

        interactions = self.missing_values(params)
        if interactions:
            interaction_request.interactions = interactions
            return interaction_request

        missions_options = [
            MissionOptionsCFs(
                patient_name=param.get("patient_name"),
                care_facilities_possible=param.get("care_facilities_possible", []),
                triage_score=param.get("triage_score"),
            )
            for param in params
        ]

        mission_final_cfs = self.return_mission_final_care_facility(missions_options)
        interaction_request.final_asset = mission_final_cfs
        interaction_request.complete = True

        return interaction_request

    def missing_values(self, params: List[Dict]) -> list[Interaction]:
        interactions = []
        for param in params:
            if (
                "care_facilities_possible" not in param
                or not param["care_facilities_possible"]
            ):
                interaction_cfs = Interaction(
                    question=f'What are the possible care facilities for {param.get("patient_name", "Unknown")}?',
                    options=[],
                )
                interactions.append(interaction_cfs)
        return interactions
