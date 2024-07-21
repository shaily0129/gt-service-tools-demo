from services.models.ModelPatient import Patient
from services.models.ModelTriageCategory import TriageCategory
from services.models.Models import TriageInteractionRequest


class Triage:
    def return_triage_categories(self, patients: list[Patient]) -> list[TriageCategory]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")
    def run_triage_algo(self, triage_interaction_request:TriageInteractionRequest)->TriageInteractionRequest:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")