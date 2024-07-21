import unittest
from services.service_triage.factory.FactoryAlgoTriage import TriageFactory, Threshold
from services.service_triage.factory.FactoryAlgoTriage import TriageAlgoName
from services.service_triage.algos.pyreason.algo_triage_pyreason.AlgoTriageLife import TriageLife, TriageScore
from services.models.ModelPatient import Patient
import numpy as np
import pyreason as pr
import numba
import os
class TestTriageFactory(unittest.TestCase):
    def setUp(self):
        self.thresholds = {
            'external_hemorrhage': Threshold(min_value=1, max_value=6),
            'tension_pneumothorax': Threshold(min_value=1, max_value=6),
            'traumatic_brain_injury': Threshold(min_value=1, max_value=6),
            'gcs': Threshold(min_value=3, max_value=15),
            'sbp': Threshold(min_value=0, max_value=219),
            'rr': Threshold(min_value=0, max_value=100),
        }

        @numba.njit(cache=True)
        def niss_ann_fn(annotations, weights):
            insult_1_acs = annotations[0][0].lower * 10
            insult_2_acs = annotations[0][1].lower * 10
            insult_3_acs = annotations[0][2].lower * 10
            niss_score = insult_1_acs * insult_1_acs + insult_2_acs * insult_2_acs + insult_3_acs * insult_3_acs
            if niss_score >= 75:
                normalized_niss_score = 1.0
            else:
                normalized_niss_score = (niss_score - 0) / (75 - 0)

            return normalized_niss_score, 1.0

        @numba.njit(cache=True)
        def rts_ann_fn(annotations, weights):
            # print(annotations)
            gcs = annotations[0][0].lower * 1000
            sbp = annotations[1][0].lower * 1000
            rr = annotations[2][0].lower * 1000

            rts_score = 0.9368 * gcs + 0.7326 * sbp + 0.2908 * rr
            normalized_rts_score = (rts_score - 3.83) / (203.57 - 3.83)

            return normalized_rts_score, 1.0

        #
        @numba.njit(cache=True)
        def life_ann_fn(annotations, weights):
            normalized_rts = annotations[0][0].lower
            normalized_niss = annotations[1][0].lower

            denormalized_niss = (normalized_niss * (75 - 0)) + 0
            denormalized_rts = (normalized_rts * (203.57 - 3.83)) + 3.83

            life_score = denormalized_rts - denormalized_niss
            # normalized_life_score = (life_score - 3.83) / (278.57 - 3.83)
            normalized_life_score = (life_score - 3.83) / (128.57 - 3.83)
            return normalized_life_score, 1.0

        pr.add_annotation_function(niss_ann_fn)
        pr.add_annotation_function(rts_ann_fn)
        pr.add_annotation_function(life_ann_fn)

        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = False
        pr.settings.store_interpretation_changes = True
        #
        current_directory = os.path.dirname(__file__)
        graphml_path = os.path.abspath(os.path.join(current_directory, '..', 'graphml_files'))
        rules_path = os.path.abspath(os.path.join(current_directory, '..', 'rules_files'))

        graphml_file = f'{graphml_path}/john_doe.graphml'
        pr.load_graphml(graphml_file)

        pr.add_rules_from_file(f'{rules_path}/life_triage_rules.txt')

    def test_create_triage_algo_pyreason(self):
        algo = TriageFactory.create_triage_algo(TriageAlgoName.LIFE, self.thresholds)
        self.assertIsNotNone(algo)
        self.assertIsInstance(algo, TriageLife)  # Ensure TriageLife instance is returned

    def test_create_triage_algo_invalid_mode(self):
        with self.assertRaises(ValueError):
            TriageFactory.create_triage_algo("invalid_mode", self.thresholds)

    def test_lifeTriage_missing_insults(self):
        patient = Patient(t=0, external_hemorrhage=np.nan, tension_pneumothorax=np.nan, traumatic_brain_injury=np.nan, gcs=12, sbp=100, rr=25)
        algo = TriageFactory.create_triage_algo(TriageAlgoName.LIFE, self.thresholds)
        triage_score_patient = algo.triage(patient)
        self.assertIsInstance(triage_score_patient, TriageScore)

    def test_lifeTriage_missing_vitals(self):
        patient = Patient(t=0, external_hemorrhage=4, tension_pneumothorax=5, traumatic_brain_injury=4, gcs=np.nan, sbp=np.nan, rr=np.nan)
        algo = TriageFactory.create_triage_algo(TriageAlgoName.LIFE, self.thresholds)
        triage_score_patient = algo.triage(patient)
        self.assertIsInstance(triage_score_patient, TriageScore)



if __name__ == '__main__':
    unittest.main()