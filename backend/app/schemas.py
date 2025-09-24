from pydantic import BaseModel
from typing import List, Optional

class MeasurementIn(BaseModel):
    n_levels: int
    pres: float
    temp: float
    psal: float

class ProfileIn(BaseModel):
    float_id: str
    n_prof: int
    latitude: float
    longitude: float
    measurements: List[MeasurementIn] = []

class ProfileOut(BaseModel):
    id: int
    float_id: str
    n_prof: int
    latitude: float
    longitude: float
    class Config:
        from_attributes = True

class ProfilesResponse(BaseModel):
    items: List[ProfileOut]
    total: int

class IngestCSVRequest(BaseModel):
    folder: str
    float_id: Optional[str] = None
