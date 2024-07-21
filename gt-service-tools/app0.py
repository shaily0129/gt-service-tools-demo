from services.service_triage.factory.FactoryAlgoTriage import TriageFactory, Threshold
from services.service_triage.factory.FactoryAlgoTriage import TriageAlgoName
from services.models.ModelPatient import Patient

if __name__ == "__main__":
    thresholds_data_algo1 = {
        'hr': Threshold(min_value=10, max_value=140),
        'spo2': Threshold(min_value=90, max_value=95),
        'temp': Threshold(min_value=0, max_value=100)
    }

    thresholds_data_algo2 = {
        'bp': Threshold(min_value=10, max_value=140),
        'glucose': Threshold(min_value=90, max_value=95),
        'gcs': Threshold(min_value=6, max_value=15)
    }

    patient1 = Patient(hr=130, spo2=85, temp=102)
    patient2 = Patient(hr=130, bp=110, glucose=90,gcs=4)

    # Triage Algo 1 - Patients 1 & 2
    print("ALGO 1")
    triage_basic_algo = TriageFactory.create_triage_algo(TriageAlgoName.BASIC,thresholds=thresholds_data_algo1)
    triage_score_patient1 = triage_basic_algo.triage(patient1)
    print(f"Patient 1 has the following Triage Score {triage_score_patient1}")
    triage_score_patient2 = triage_basic_algo.triage(patient2)
    print(f"Patient 2 has the following Triage Score {triage_score_patient2}")

    # Triage Algo 2 - Patients 1 & 2
    print("")
    print("ALGO 2")
    triage_basic2_algo = TriageFactory.create_triage_algo(TriageAlgoName.BASIC2, thresholds=thresholds_data_algo2)
    triage_score_patient1 = triage_basic2_algo.triage(patient1)
    print(f"Patient 1 has the following Triage Score {triage_score_patient1}")
    triage_score_patient2 = triage_basic2_algo.triage(patient2)
    print(f"Patient 2 has the following Triage Score {triage_score_patient2}")
