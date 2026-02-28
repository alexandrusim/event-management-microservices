from pydantic import BaseModel, Field
from typing import Optional


class EventCreate(BaseModel):
    nume: str = Field(..., min_length=1)
    locatie: Optional[str] = None
    descriere: Optional[str] = None
    numarLocuri: Optional[int] = None

class Event(EventCreate):
    id: int
    id_owner: Optional[int] = None

    class Config:
        from_attributes = True


class PachetCreate(BaseModel):
    nume: str = Field(..., min_length=1)
    locatie: Optional[str] = None
    descriere: Optional[str] = None
    numarLocuri: Optional[int] = None


class Pachet(PachetCreate):
    id: int
    id_owner: Optional[int] = None

    class Config:
        from_attributes = True


class Bilet(BaseModel):
    COD: str
    PachetID: Optional[int] = None
    EvenimentID: Optional[int] = None

    class Config:
        from_attributes = True

class EventInPachet(BaseModel):
    event_id: int