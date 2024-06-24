import unittest
from services.service_triage.factory.FactoryAlgoTriage import TriageFactory, Threshold
from services.service_triage.factory.FactoryAlgoTriage import TriageAlgoName
from services.service_triage.algos.vanilla.algo_triage_basic.AlgoBasicTriage import BasicTriage
from services.service_triage.algos.vanilla.algo_triage_basic2.AlgoBasicTriage2 import BasicTriage2


class TestTriageFactory(unittest.TestCase):
    def setUp(self):
        self.thresholds = {
            'hr': Threshold(min_value=10, max_value=140),
            'spo2': Threshold(min_value=90, max_value=95),
            'temp': Threshold(min_value=0, max_value=100)
        }


    def test_create_triage_algo_basic(self):
        algo = TriageFactory.create_triage_algo(TriageAlgoName.BASIC, self.thresholds)
        self.assertIsNotNone(algo)
        self.assertIsInstance(algo, BasicTriage)  # Ensure BasicTriage instance is returned

    def test_create_triage_algo_basic2(self):
        algo = TriageFactory.create_triage_algo(TriageAlgoName.BASIC2, self.thresholds)
        self.assertIsNotNone(algo)
        self.assertIsInstance(algo, BasicTriage2)  # Ensure BasicTriage2 instance is returned

    def test_create_triage_algo_invalid_mode(self):
        with self.assertRaises(ValueError):
            TriageFactory.create_triage_algo("invalid_mode", self.thresholds)



if __name__ == '__main__':
    unittest.main()