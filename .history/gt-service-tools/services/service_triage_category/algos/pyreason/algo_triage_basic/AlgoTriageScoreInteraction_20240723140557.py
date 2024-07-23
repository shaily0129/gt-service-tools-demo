from services.service_triage.AlgoTriage import Triage
from services.models.ModelTriageScore import TriageScore, RationaleRecord, Vital
from services.models.ModelPatient import Patient
from datetime import datetime
from typing import List, Dict
from services.models.Models import Interaction, TriageInteractionRequest
from caching.CacheRedis import RedisManager


class TriageScoreInteraction(Triage):

    def __init__(self, thresholds: Dict):
        self.thresholds = thresholds

    def validate_thresholds(self, value, threshold):
        if value > threshold.max_value:
            raise ValueError(f"{value} cannot be greater than {threshold.max_value}")
        elif value < threshold.min_value:
            raise ValueError(f"{value} cannot be less than {threshold.min_value}")

    def get_normalized_gcs(self, gcs):
        if gcs == 3:
            return 0algo
        if gcs in [4, 5]:
            return 1
        if gcs in [6, 7, 8]:
            return 2
        if gcs in [9, 10, 11, 12]:
            return 3
        if gcs in [13, 14, 15]:
            return 4

    def get_normalized_sbp(self, sbp):
        if sbp == 0:
            return 0
        if sbp >= 1 and sbp <= 49:
            return 1
        if sbp >= 50 and sbp <= 75:
            return 2
        if sbp >= 76 and sbp <= 89:
            return 3
        if sbp >= 90:
            return 4

    def get_normalized_rr(self, rr):
        if rr == 0:
            return 0
        if rr >= 1 and rr <= 5:
            return 1
        if rr >= 6 and rr <= 9:
            return 2
        if rr >= 10 and rr <= 29:
            return 3
        if rr >= 30:
            return 4

    def rts_score(self, vitals_dict):
        if (
            "gcs" not in vitals_dict
            or "sbp" not in vitals_dict
            or "rr" not in vitals_dict
        ):
            return None

        normalized_gcs = self.get_normalized_gcs(vitals_dict["gcs"])
        normalized_sbp = self.get_normalized_sbp(vitals_dict["sbp"])
        normalized_rr = self.get_normalized_rr(vitals_dict["rr"])

        return (
            0.9368 * normalized_gcs + 0.7326 * normalized_sbp + 0.2908 * normalized_rr
        )

    def niss_score(self, insult_dict):
        ais_scores_all = []
        niss_score = 0
        if not insult_dict:
            return None
        for insult, ais in insult_dict.items():
            ais_scores_all.append(ais)
        top_3_ais_scores = sorted(ais_scores_all, reverse=True)[:3]
        for ais_score in top_3_ais_scores:
            niss_score += ais_score * ais_score
        return niss_score

    def triage(self, patients: List[Patient]) -> List[TriageScore]:
        triage_scores = []
        keys_all = self.thresholds.keys()
        keys_all_insults = list(set(keys_all).difference(set(["gcs", "sbp", "rr"])))
        keys_all_vitals = ["gcs", "sbp", "rr"]

        for patient in patients:
            record = patient.physiology_record
            patient_insults_keys = [key for key in keys_all_insults if key in record]
            patient_vitals_keys = [key for key in keys_all_vitals if key in record]
            patient_insults_dict = {}
            patient_vitals_dict = {}

            rationale_records = []
            score = 0.0

            if not record:
                triage_scores.append(
                    TriageScore(
                        patient_name=record.get("name", "Unknown"),
                        score=0.0,
                        rationale=rationale_records,
                        datetime_seconds=int(datetime.now().timestamp()),
                        algo_name="LifeTriage",
                        interaction=None,
                        confidence=0.0,  # Set a default value for confidence
                    )
                )
                continue

            for vital_name, threshold in self.thresholds.items():
                if vital_name in record:
                    value = record[vital_name]
                    self.validate_thresholds(value, threshold)
                    rationale_records.append(
                        RationaleRecord(
                            vital=Vital(name=vital_name, value=value),
                            score=1.0,
                            threshold=threshold,
                        )
                    )

            for patient_insult_key in patient_insults_keys:
                patient_insults_dict[patient_insult_key] = record[patient_insult_key]

            for patient_vital_key in patient_vitals_keys:
                patient_vitals_dict[patient_vital_key] = record[patient_vital_key]

            niss_score = self.niss_score(patient_insults_dict)
            rts_score = self.rts_score(patient_vitals_dict)

            if niss_score is not None and rts_score is not None:
                algo_name = "LIFE"
                score = 100 - 0.5 * niss_score - 7 * rts_score
            elif niss_score is None and rts_score is not None:
                algo_name = "RTS"
                score = 100 - (rts_score / 54.8856) * 100
            elif niss_score is not None and rts_score is None:
                algo_name = "NISS"
                score = 100 - (niss_score / 108) * 100
            else:
                algo_name = "None"
                score = 0.0

            triage_scores.append(
                TriageScore(
                    patient_name=record.get("name", "Unknown"),
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name=algo_name,
                    score=score,
                    confidence=1,
                    rationale=rationale_records,
                    interaction=None,
                )
            )
        return triage_scores

    def run_triage_algo(
        self, triage_interaction_request: TriageInteractionRequest
    ) -> TriageInteractionRequest:
        parameters = triage_interaction_request.params

        # Check for missing values
        interactions = self.missing_values(parameters)
        if len(interactions) > 0:
            triage_interaction_request.interactions = interactions
            return triage_interaction_request

        # Create Patient object
        patient = Patient(**parameters)

        # Calculate Triage Score
        triage_scores = self.triage([patient])
        if triage_scores:
            triage_interaction_request.triage_score = triage_scores[0]
        triage_interaction_request.complete = True
        triage_interaction_request.interactions = None

        # Cache result
        caching_manager = RedisManager()
        # key = f"tools-triage-{triage_interaction_request.request_id}"
        key = f"tools-triage-{triage_interaction_request.request_id}-{triage_interaction_request.patient_id}"
        caching_manager.save_json(key, triage_interaction_request.json())

        return triage_interaction_request

    def missing_values(self, params: Dict) -> List[Interaction]:
        interactions = []
        # No mandatory fields

        return interactions
