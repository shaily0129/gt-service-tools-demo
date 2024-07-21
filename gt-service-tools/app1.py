
import time

from services.service_triage.factory.FactoryAlgoTriage import TriageFactory, Threshold
from services.service_triage.factory.FactoryAlgoTriage import TriageAlgoName
from services.models.ModelPatient import Patient

import pandas as pd
import pyreason as pr
import os
import numba


if __name__ == "__main__":

    thresholds_data_algo3 = {
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
    # Get the absolute path of the current script
    script_path = os.path.abspath(__file__)

    # Get the directory containing the script
    script_dir = os.path.dirname(script_path)

    folder_name = 'services/service_triage/algos/pyreason/graphml_files'
    folder_path = os.path.join(script_dir, folder_name)
    graphml_file = f'{folder_path}/john_doe.graphml'
    pr.load_graphml(graphml_file)


    folder_name = 'services/service_triage/algos/pyreason/rules_files'
    folder_path = os.path.join(script_dir, folder_name)
    pr.add_rules_from_file(f'{folder_path}/life_triage_rules.txt')


    temp_dict = {}
    '''
    Uncomment user story as required:
    
    User story 1 : Missing GCS value.
    User story 2: All data available to compute LIFE score, but vitals are changing for timestamps.
    User story 3: Vitals missing due to damaged sensors.
    User story 4: Vitals available initially but then stopped after some timestamp due to some damage to sensors.
    User story 5: Insults data missing as mic is broken.
    '''
    time_series_file = 'data/triage/user_story_1_missing_gcs.csv'
    # time_series_file = 'user_story_2_all_available.csv'
    # time_series_file = 'user_story_3_missing_vitals.csv'
    # time_series_file = 'user_story_4_failed vital_data.csv'
    # time_series_file = 'user_story_5_missing_insults.csv'
    df = pd.read_csv(time_series_file)
    for index, row in df.iterrows():
        patient3 = Patient(t=row['timestamp'], external_hemorrhage=row['external_hemorrhage'], tension_pneumothorax=row['tension_pneumothorax'], traumatic_brain_injury=row['traumatic_brain_injury'],
                           gcs=row['gcs'], sbp=row['sbp'], rr=row['rr'])
        # Triage Algo 3 - Patient 3
        print("")
        print("ALGO 3- LIFETriage")
        triage_life_algo = TriageFactory.create_triage_algo(TriageAlgoName.LIFE, thresholds=thresholds_data_algo3)
        start_time = time.time()
        triage_score_patient3 = triage_life_algo.triage(patient3)
        end_time = time.time()
        print(f'Time to compute triage score: {end_time - start_time}')
        print(f"Patient 3 has the following LIFE Triage Score {triage_score_patient3}")



