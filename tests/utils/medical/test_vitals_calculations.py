
import pytest
import os
# import sys
# import importlib

import importlib.util
import sys
# Append the project directory to sys.path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gt-service-tools'))
if project_dir not in sys.path:
    sys.path.append(project_dir)
from utils.medical import vitals_calculations as module

class TestCalculateMeanArterialPressure:
    def setup_method(self, method):
        self.mean_arterial_pressure = module.VitalsCalculations().MeanArterialPressure().calculate_map
        

    def test_mean_arterial_pressure(self):
        test_cases = [
            {"sys_bp": 120, "dia_bp": 80, "expected": 93.33, "exception": None, "test": "Integers"},
            {"sys_bp": 120.00, "dia_bp": 80.00, "expected": 93.33, "exception": None, "test": "Floats"},
            {"sys_bp": "120", "dia_bp": "80", "expected": 93.33, "exception": None, "test": "Integers as <Strings>"},
            {"sys_bp": "120.00", "dia_bp": "80.00", "expected": 95.33, "exception": None, "test": "Floats as <Strings>"},
            {"sys_bp": None, "dia_bp": 80, "expected": None, "exception": ValueError, "test": "Missing Systolic"},
            {"sys_bp": 120, "dia_bp": None, "expected": None, "exception": ValueError, "test": "Missing Diastolic"},
            {"sys_bp": "Sys BP is 120", "dia_bp": 80, "expected": None, "exception": ValueError, "test": "Invalid String"},
            {"sys_bp": 80, "dia_bp": 120, "expected": None, "exception": ValueError, "test": "Systolic < Diastolic"},
        ]

        print("")
        print("Testing 'calculate_map' function")
        for case in test_cases:
            status_msg = "✓"
            try:
                if case["exception"]:
                    with pytest.raises(case["exception"]):
                        assert self.mean_arterial_pressure(case["sys_bp"], case["dia_bp"]) == case["expected"]
                else:
                    assert self.mean_arterial_pressure(case["sys_bp"], case["dia_bp"]) == pytest.approx(case["expected"], 0.01), f"Test Failed: {case['test']}"
            except AssertionError:
                status_msg = "✕"
            
            if status_msg == '✕':
                print(f"\033[31m  {status_msg} - {case['test']} test\033[0m")
            else:
                print(f"\033[92m  {status_msg} - {case['test']} test\033[0m")

if __name__ == '__main__':
    pytest.main(['-s'])