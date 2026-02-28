from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class TicketAdd(BaseModel):
    cod: str = Field(..., description="Codul unic al biletului de adaugat")

class ClientBase(BaseModel):
    email: str = Field(..., pattern=r".+@.+\..+")
    prenume_nume: Optional[str] = None
    link_uri_social_media: Optional[Dict[str, str]] = None

class ClientCreate(ClientBase):
    pass

class ClientInDB(ClientBase):
    user_id: int
    lista_bilete: List[str] = []

    class Config:
        from_attributes = True