from typing import Dict, List, Optional, Any

from pydantic import BaseModel
from pydantic import BaseModel, ValidationError, field_validator

from services.models.ModelTriageCategory import TriageCategory
from services.models.ModelTriageScore import TriageScore
from services.models.ModelPatientMatrix import PatientMatrix
from services.models.ModelMissionFinalAssets import MissionFinalAssets


class InteractionOption(BaseModel):
    sequence: int
    option_name: str
    option_description: str


class Interaction(BaseModel):
    variable_name: str
    variable_type: str
    question: str
    options: Optional[List[InteractionOption]]
    answer: Optional[str]
    complete: bool = False


class InteractionRequest(BaseModel):
    request_id: str
    params: dict = {}
    interactions: Optional[List[Interaction]] = None
    complete: Optional[bool] = False


class BookingInteractionRequest(InteractionRequest):
    booking_id: Optional[str] = None


class TriageInteractionRequest(InteractionRequest):
    patient_id: Optional[str] = None
    triage_score: Optional[TriageScore] = None


class TriageInteractionRequest1(InteractionRequest):
    patient_id: Optional[str] = None
    triage_category: Optional[TriageCategory] = None


class PatientMatrixInteractionRequest(InteractionRequest):
    patient_id: Optional[str] = None
    patient_matrix: Optional[PatientMatrix] = None


class MissionOptionsAssets(BaseModel):
    patient_name: str
    assets_possible: List[str]
    triage_score: int


class MissionInteractionRequest(BaseModel):
    pa_id: str
    params: List[Dict[str, Any]]
    mission_final_assets: List[MissionFinalAssets] = []
    complete: bool = False


class EvacStrandedPersonnelInteractionRequest(InteractionRequest):
    booking_id: Optional[str] = None
