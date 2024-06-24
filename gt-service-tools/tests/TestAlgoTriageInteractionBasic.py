import unittest
import numpy as np
from services.models.ModelPatient import Patient

from services.service_triage.algos.vanilla.algo_triage_interaction_basic.AlgoTriageInteractionBasic import \
    BasicTriageWithInteraction


class TestAlgoTriageWithInteractionBasic(unittest.TestCase):
    def test_result_not_empty(self):

        p = Patient(t=0, external_hemorrhage=4, tension_pneumothorax=5, traumatic_brain_injury=4, gcs=np.nan,
                    sbp=np.nan, rr=np.nan)

        algo = BasicTriageWithInteraction()
        result = algo.triage(patient=p)

        self.assertIsNotNone(result)

        # Assertion 1: Check if question_obj is an instance of Interaction
        # self.assertIsInstance(question_obj, Interaction)
        #
        # # Assertion 2: Check if the question attribute matches the provided question in the JSON
        # self.assertEqual(question_obj.question, json_object["question"])
        #
        # # Assertion 3: Check if options attribute is a list
        # self.assertIsInstance(question_obj.options, list)
        #
        # # Assertion 4: Check if each option is an instance of Option class
        # for option in question_obj.options:
        #     self.assertIsInstance(option, Option)

        # # Assertion 5: Check if attributes of each Option object match the values in the JSON
        # for i, option in enumerate(question_obj.options):
        #     self.assertEqual(option.input, json_object["options"][i]["input"])
        #     self.assertEquals(option.description, json_object["options"][i]["description"])



