from services.service_triage_category.AlgoTriageCategory import Triage

from services.models.ModelTriageCategory import (
    TriageCategory,
    RationaleRecord,
    TriageScore,
)
from services.models.ModelPatient import Patient


from datetime import datetime
import networkx as nx
import pyreason as pr
import os
import math

from caching.CacheRedis import RedisManager
from services.models.Models import (
    Interaction,
    InteractionOption,
    TriageInteractionRequest,
    InteractionRequest,
)
from services.service_triage_category import AlgoTriageCategory
import inspect
import string
import random
from typing import List, Optional, Dict


class TriageCategoryBasic(Triage):

    def __init__(self, thresholds=None):
        self.thresholds = thresholds
        self.interpretation = None
        self.next_time = 0

    def __generate_patient_id(self):
        # Define the character set from which to generate the string
        characters = string.digits  # This includes '0123456789'

        # Generate a random 8-character string
        random_string = "".join(random.choice(characters) for _ in range(8))

        return random_string

    def create_pyreason_graph(self, patients: list[Patient]):
        g = nx.DiGraph()

        # Add triage scores
        for i in range(101):
            if i in range(31):
                g.add_node(str(i), type_score="1,1", zero_thirty="1,1")
            elif i in range(31, 51):
                g.add_node(str(i), type_score="1,1", thirty_fifty="1,1")
            elif i in range(51, 71):
                g.add_node(str(i), type_score="1,1", fifty_seventy="1,1")
            elif i in range(71, 91):
                g.add_node(str(i), type_score="1,1", seventy_ninety="1,1")
            else:
                g.add_node(str(i), type_score="1,1", ninety_hundred="1,1")

        # Add triage categories
        g.add_node(
            "expectant", triage_category_id=2, type_triage_category_expectant="1,1"
        )
        g.add_node(
            "immediate", triage_category_id=3, type_triage_category_immediate="1,1"
        )
        g.add_node("urgent", triage_category_id=4, type_triage_category_urgent="1,1")
        g.add_node("delayed", triage_category_id=5, type_triage_category_delayed="1,1")
        g.add_node("minor", triage_category_id=6, type_triage_category_minor="1,1")
        g.add_node(
            "uninjured", triage_category_id=7, type_triage_category_uninjured="1,1"
        )

        categories = [
            "expectant",
            "immediate",
            "urgent",
            "delayed",
            "minor",
            "uninjured",
        ]
        # Add casualties
        for index, patient in enumerate(patients):
            record = patient.physiology_record
            g.add_node(record["name"], casualty_id=index + 2, type_casualty="1,1")

            for category in categories:
                # Edge casualty,category
                g.add_edge(record["name"], category, triage_category="0,1")
            for i in range(101):
                g.add_edge(record["name"], str(i), triage_score="0,1")

        return g

    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_triage_categories(self, patients: list[Patient]) -> list[TriageCategory]:

        triage_categories = []
        # Set pyreason settings

        graph = self.create_pyreason_graph(patients)
        graphml_path = "pyreason_input_graph_triage_scores.graphml"
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)


        rules_path = "rules_triage_score_to_triage_category.txt"
        self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
        rules_path = os.path.join(current_script_directory, rules_path)

        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True

        pr.load_graphml(graphml_path)
        pr.add_rules_from_file(rules_path)

        # Reason at t=0
        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1

        edge_facts = []
        node_facts = []

        for index, patient in enumerate(patients):
            record = patient.physiology_record
            fact_cas_score = pr.fact_edge.Fact(
                f"f_cas_score_{index}",
                (record["name"], str(math.floor(float(record["triage_score"])))),
                pr.label.Label("triage_score"),
                pr.interval.closed(1, 1),
                self.next_time,
                self.next_time,
            )
            edge_facts.append(fact_cas_score)

        # Reason at t=1
        self.interpretation = pr.reason(again=True, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = "traces_t1_triage_score_to_triage_category"
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        field = "triage_category"
        df_category = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_category):
            if not df[field].empty:
                for i in range(len(df["component"])):
                    if df[field][i] == [1, 1]:
                        patient_name = df["component"][i][0]
                        category = df["component"][i][1]
                        triage_categories.append(
                            TriageCategory(
                                patient_name=patient_name,
                                datetime_seconds=int(datetime.now().timestamp()),
                                algo_name="pyreason_basic",
                                category=category,
                                confidence=1,
                                rationale=None,
                                interaction=None,
                            )
                        )
        return triage_categories

    def missing_values(self, params: Dict) -> List[Interaction]:
        interactions = []
        # ***************** MANDATORY *****************
        # Check for 'name'
        if "name" not in params or not params["name"].strip():
            interaction_name = Interaction(
                variable_name="name",
                variable_type="str",
                question="What is your name?",
                options=None,
                answer=None,
                complete=False,
            )
            interactions.append(interaction_name)
        else:
            # Check for 'age'
            if "triage_score" not in params or not params["triage_score"].strip():
                interaction_age = Interaction(
                    variable_name="triage_score",
                    variable_type="str",
                    question=f'What is the triage score of {params.get("name")}? Enter any number between 0 and 100: ',
                    options=None,
                    answer=None,
                    complete=False,
                )
                interactions.append(interaction_age)

        return interactions

    def run_triage_algo(
        self, triage_interaction_request: TriageInteractionRequest
    ) -> TriageInteractionRequest:
        # Step1 - Get the requested params list
        parameters = triage_interaction_request.params

        # Step 2 - Create the interactions for mandatory variables
        interactions = self.missing_values(parameters)
        if len(interactions) > 0:
            triage_interaction_request.interactions = interactions
            return triage_interaction_request

        # Step3 - Complete the interaction
        triage_interaction_request.patient_id = self.__generate_patient_id()
        triage_interaction_request.triage_category = self.return_triage_categories(
            patients=[
                Patient(
                    name=triage_interaction_request.params.get("name"),
                    triage_score=triage_interaction_request.params.get("triage_score"),
                )
            ]
        )[0]
        triage_interaction_request.interactions = None
        triage_interaction_request.complete = (
            True  # Important!  Without this we get stuck
        )
        caching_manager = RedisManager()
        # KEY = booking_interaction_request.request_id
        # caching_manager.save_json(key, booking_interaction_request.json())
        return triage_interaction_request
