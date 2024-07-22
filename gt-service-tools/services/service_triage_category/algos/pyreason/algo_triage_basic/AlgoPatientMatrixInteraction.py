# from services.models.ModelPatient import Patient
# from services.models.Models import PatientMatrixInteractionRequest
# from services.service_patient_priority_matrix.factory.FactoryAlgo import (
#     TriagecategoryToPatientmatrixFactory,
#     TriagecategoryToPatientMatrixAlgoName,
# )
# from caching.CacheRedis import RedisManager
# from typing import List


# class PatientMatrixInteraction:
#     def __init__(self):
#         pass

#     def run_patient_matrix_algo(
#         self, interaction_request: PatientMatrixInteractionRequest
#     ) -> PatientMatrixInteractionRequest:
#         parameters = interaction_request.params

#         # Create Patient objects
#         patients = [Patient(**params) for params in parameters.get("patients", [])]

#         # Calculate Patient Matrix
#         algo_patient_matrix = TriagecategoryToPatientmatrixFactory.create_triageCategory_to_patientMatrix_algo(
#             mode=TriagecategoryToPatientMatrixAlgoName.BASIC
#         )
#         matrix_all_patients = algo_patient_matrix.return_patient_priority_matrix(
#             patients
#         )
#         interaction_request.patient_matrix = matrix_all_patients
#         interaction_request.complete = True

#         # Cache result
#         caching_manager = RedisManager()
#         key = f"tools-patient-matrix-{interaction_request.request_id}"
#         caching_manager.save_json(key, interaction_request.json())

#         return interaction_request


import logging
from services.service_patient_priority_matrix.AlgoPatientPriorityMatrix import (
    PatientPriority,
)
from services.models.ModelPatientMatrix import PatientMatrix
from services.models.ModelPatient import Patient
from datetime import datetime
import networkx as nx
import pyreason as pr
import os
from typing import List, Dict
from services.models.Models import (
    Interaction,
    InteractionOption,
    PatientMatrixInteractionRequest,
)

logger = logging.getLogger(__name__)


class PatientMatrixInteraction(PatientPriority):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def __generate_request_id(self):
        import string
        import random

        return "".join(random.choice(string.digits) for _ in range(8))

    def create_pyreason_graph(self, patients_cat: list[Patient]):
        g = nx.DiGraph()

        # Add triage categories
        categories = [
            "expectant",
            "immediate",
            "urgent",
            "delayed",
            "minor",
            "uninjured",
        ]
        for category in categories:
            g.add_node(
                category,
                triage_category_id=categories.index(category) + 2,
                type_triage_category=f"1,1",
            )

        # Add priorities 0 to 6
        for i in range(7):
            g.add_node(str(i), priority=f"1,1")

        # Add casualties
        for index, patient in enumerate(patients_cat):
            record = patient.physiology_record
            patient_name = record["name"]
            patient_category = record["category"]
            g.add_node(
                patient_name,
                casualty_id=index + 2,
                type_casualty="1,1",
                litter="0,0",
                ambulatory="1,1",
                medevac_needed="0,0",
                evac_needed="0,0",
                resupply_needed="0,0",
            )

            # Edge casualty, category
            g.add_edge(patient_name, patient_category, triage_category="1,1")

            # Target edge :: casualty, priority
            for i in range(7):
                g.add_edge(
                    patient_name,
                    str(i),
                    medevac_priority="0,0",
                    evac_priority="0,0",
                    resupply_priority="0,0",
                )

        return g

    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_patient_priority_matrix(
        self, patients_categories: list[Patient]
    ) -> list[PatientMatrix]:
        patients_priority_matrices = []
        # Set pyreason settings

        graph = self.create_pyreason_graph(patients_categories)
        graphml_path = "pyreason_input_graph_triage_categories.graphml"
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = "rules_triage_category_to_patient_priority_matrix.txt"
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
        folder_name = "traces_t0_triage_category_to_patient_priority_matrix"
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        patient_detail = {}
        fields = [
            "litter",
            "ambulatory",
            "medevac_needed",
            "evac_needed",
            "resupply_needed",
        ]
        for field in fields:
            df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
            for t, df in enumerate(df_outer):
                if not df[field].empty:
                    for i in range(len(df["component"])):
                        if df["component"][i] not in patient_detail:
                            patient_detail[df["component"][i]] = {}
                        patient_detail[df["component"][i]][field] = df[field][i] == [
                            1,
                            1,
                        ]

        priority_fields = ["medevac_priority", "evac_priority", "resupply_priority"]
        for field in priority_fields:
            df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
            for t, df in enumerate(df_outer):
                if not df[field].empty:
                    for i in range(len(df["component"])):
                        if df["component"][i][0] not in patient_detail:
                            patient_detail[df["component"][i][0]] = {}
                        try:
                            patient_detail[df["component"][i][0]][field] = int(
                                df["component"][i][1]
                            )  # Ensure this is an integer
                        except ValueError as e:
                            logger.error(
                                f"Error parsing priority value for {df['component'][i][0]}: {e}"
                            )
                            patient_detail[df["component"][i][0]][
                                field
                            ] = 0  # Default to 0 if parsing fails

        for p_name, p_details in patient_detail.items():
            patients_priority_matrices.append(
                PatientMatrix(
                    patient_name=p_name,
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name="pyreason_basic",
                    litter=p_details.get("litter", False),
                    ambulatory=p_details.get("ambulatory", False),
                    medevac_needed=p_details.get("medevac_needed", False),
                    medevac_priority=p_details.get("medevac_priority", 0),
                    evac_needed=p_details.get("evac_needed", False),
                    evac_priority=p_details.get("evac_priority", 0),
                    resupply_needed=p_details.get("resupply_needed", False),
                    resupply_priority=p_details.get("resupply_priority", 0),
                    confidence=1.0,
                    rationale=None,
                    interaction=None,
                )
            )
        return patients_priority_matrices

    def run_patient_matrix_algo(
        self, interaction_request: PatientMatrixInteractionRequest
    ) -> PatientMatrixInteractionRequest:
        parameters = interaction_request.params

        # Generate interactions if parameters are missing
        interactions = self.missing_values(parameters)
        if len(interactions) > 0:
            interaction_request.interactions = interactions
            return interaction_request

        # Generate request ID if not provided
        if not interaction_request.request_id:
            interaction_request.request_id = self.__generate_request_id()

        # Compute patient matrix based on provided category
        patients = [
            Patient(
                name=interaction_request.params.get("name", "Unknown"),
                category=interaction_request.params.get("category"),
            )
        ]

        interaction_request.patient_matrix = self.return_patient_priority_matrix(
            patients
        )
        interaction_request.interactions = None
        interaction_request.complete = True

        return interaction_request

    def missing_values(self, params: Dict) -> List[Interaction]:
        interactions = []
        # Check for 'category'
        if "category" not in params or not params["category"].strip():
            interaction = Interaction(
                variable_name="category",
                variable_type="str",
                question="What is the category of the patient?",
                options=[
                    InteractionOption(
                        sequence=0,
                        option_name="expectant",
                        option_description="expectant category",
                    ),
                    InteractionOption(
                        sequence=1,
                        option_name="immediate",
                        option_description="immediate category",
                    ),
                    InteractionOption(
                        sequence=2,
                        option_name="urgent",
                        option_description="urgent category",
                    ),
                    InteractionOption(
                        sequence=3,
                        option_name="delayed",
                        option_description="delayed category",
                    ),
                    InteractionOption(
                        sequence=4,
                        option_name="minor",
                        option_description="minor category",
                    ),
                    InteractionOption(
                        sequence=5,
                        option_name="uninjured",
                        option_description="uninjured category",
                    ),
                ],
                answer=None,
                complete=False,
            )
            interactions.append(interaction)
        return interactions
