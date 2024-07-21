from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4

class Threshold(BaseModel):
    min_value: int
    max_value: int


class Patient(BaseModel):
    id: Optional[UUID] = None
    name: str
    external_hemorrhage: Optional[int] = None
    tension_pneumothorax: Optional[int] = None
    traumatic_brain_injury: Optional[int] = None
    concussion: Optional[int] = None
    cerebral_contusion: Optional[int] = None
    subarachnoid_hemorrhage: Optional[int] = None
    epidural_hematoma: Optional[int] = None
    nasal_fracture: Optional[int] = None
    orbital_fracture: Optional[int] = None
    le_fort_II_fracture: Optional[int] = None
    rib_fracture: Optional[int] = None
    lung_contusion: Optional[int] = None
    flail_chest: Optional[int] = None
    aortic_laceration: Optional[int] = None
    minor_liver_laceration: Optional[int] = None
    splenic_laceration: Optional[int] = None
    liver_hematoma: Optional[int] = None
    pancreatic_transection: Optional[int] = None
    radius_ulna_fracture: Optional[int] = None
    femur_fracture: Optional[int] = None
    knee_dislocation: Optional[int] = None
    traumatic_amputation_below_knee: Optional[int] = None
    traumatic_amputation_above_knee: Optional[int] = None
    burn: Optional[int] = None
    gcs: Optional[int] = None
    sbp: Optional[int] = None
    rr: Optional[int] = None


class PatientUpdateRequest(BaseModel):
    name: Optional[str] = None
    external_hemorrhage: Optional[int] = None
    tension_pneumothorax: Optional[int] = None
    traumatic_brain_injury: Optional[int] = None
    concussion: Optional[int] = None
    cerebral_contusion: Optional[int] = None
    subarachnoid_hemorrhage: Optional[int] = None
    epidural_hematoma: Optional[int] = None
    nasal_fracture: Optional[int] = None
    orbital_fracture: Optional[int] = None
    le_fort_II_fracture: Optional[int] = None
    rib_fracture: Optional[int] = None
    lung_contusion: Optional[int] = None
    flail_chest: Optional[int] = None
    aortic_laceration: Optional[int] = None
    minor_liver_laceration: Optional[int] = None
    splenic_laceration: Optional[int] = None
    liver_hematoma: Optional[int] = None
    pancreatic_transection: Optional[int] = None
    radius_ulna_fracture: Optional[int] = None
    femur_fracture: Optional[int] = None
    knee_dislocation: Optional[int] = None
    traumatic_amputation_below_knee: Optional[int] = None
    traumatic_amputation_above_knee: Optional[int] = None
    burn: Optional[int] = None
    gcs: Optional[int] = None
    sbp: Optional[int] = None
    rr: Optional[int] = None

