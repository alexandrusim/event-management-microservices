from typing import List, Dict
from models import Event, EventCreate

_events: List[Dict] = [
    {"id": 1, "id_owner": 1, "nume": "Concert Coldplay", "locatie": "Cluj Arena", "descriere": "Open-air 2025", "numarLocuri": 50000},
    {"id": 2, "id_owner": 2, "nume": "Jazz Festival Iasi", "locatie": "Iasi", "descriere": "Festival de jazz", "numarLocuri": 800}
]

def list_events() -> List[Dict]:
    return _events

def get_event_by_id(event_id: int):
    return next((e for e in _events if e["id"] == event_id), None)

def add_event(ev: EventCreate) -> Dict:
    new_id = max((e["id"] for e in _events), default=0) + 1
    new = ev.dict()
    new["id"] = new_id
    new["id_owner"] = None
    _events.append(new)
    return new

def update_event(event_id: int, ev: dict):
    e = get_event_by_id(event_id)
    if not e:
        return None
    # update only provided fields
    for k,v in ev.items():
        if k in e and k != "id":
            e[k] = v
    return e

def delete_event(event_id: int) -> bool:
    global _events
    before = len(_events)
    _events = [e for e in _events if e["id"] != event_id]
    return len(_events) < before
