from typing import Dict, List, Optional, Any

from pydantic import BaseModel
from pydantic import BaseModel, ValidationError, field_validator

from services.models.ModelTriageCategory import TriageCategory
from services.models.ModelTriageScore import TriageScore
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.ModelPatientMatrix import PatientMatrix


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


# class TriageInteractionRequest(InteractionRequest):
#     patient_id: Optional[str] = None
#     triage_score: Optional[TriageScore] = None


class TriageInteractionRequest(InteractionRequest):
    patient_id: str  # Mandatory field
    triage_score: Optional[TriageScore] = None


class TriageInteractionRequest1(InteractionRequest):
    patient_id: Optional[str] = None
    triage_category: Optional[TriageCategory] = None


# class FinalAssetInteractionRequest(InteractionRequest):
#     patient_id: Optional[str] = None
#     final_asset: Optional[MissionFinalAssets] = None


class FinalAssetInteractionRequest(BaseModel):
    request_id: str
    params: List[dict]  # Adjusted to expect a list of dictionaries
    patient_id: Optional[str] = None
    final_asset: Optional[MissionFinalAssets] = None
    complete: bool = False
    interactions: Optional[List[Interaction]] = None


class PatientMatrix(BaseModel):
    patient_name: Optional[str]
    datetime_seconds: int
    algo_name: str
    litter: bool
    ambulatory: bool
    medevac_needed: bool
    medevac_priority: Optional[int]
    evac_needed: bool
    evac_priority: Optional[int]
    resupply_needed: bool
    resupply_priority: Optional[int]
    confidence: float
    rationale: Optional[List[Dict]] = None
    interaction: Optional[Interaction] = None


class PatientMatrixInteractionRequest(BaseModel):
    request_id: str
    patient_id: str
    params: Dict[str, str]
    interactions: Optional[List[Interaction]] = None
    complete: Optional[bool] = False
    patient_matrix: Optional[PatientMatrix] = None


class EvacStrandedPersonnelInteractionRequest(InteractionRequest):
    booking_id: Optional[str] = None
