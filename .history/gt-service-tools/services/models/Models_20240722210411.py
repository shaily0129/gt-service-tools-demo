from datetime import datetime
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



# class MissionInteractionRequest(BaseModel):
#     request_id: str
#     params: List[Dict[str, Any]]
#     mission_final_assets: List[MissionFinalAssets] = []
#     complete: bool = False

class MissionOptionsAssets(BaseModel):
    patient_name: Optional[str]
    assets_possible: list
    triage_score: Optional[float] = None

class MissionFinalAssets(BaseModel):
    patient_name: Optional[str]
    datetime_seconds: int = int(datetime.now().timestamp())
    algo_name: str = 'pyreason_basic'
    asset_final: str = ''
    asset_details: Optional[dict] = None
    confidence: float = 1.0
    rationale: Optional[List[Any]] = None
    interaction: Optional[Any] = None

class MissionInteractionRequest(BaseModel):
    request_id: str
    params: List[MissionOptionsAssets]
    mission_final_assets: List[MissionFinalAssets] = []
    complete: bool = False

class EvacStrandedPersonnelInteractionRequest(InteractionRequest):
    booking_id: Optional[str] = None
