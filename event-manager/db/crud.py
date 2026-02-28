from sqlalchemy.orm import Session
from sqlalchemy import func
from .models_db import Eveniment, Pachet, Bilet
from models import EventCreate, PachetCreate
from fastapi import HTTPException
import uuid


# Functii Eveniment

def list_events(db: Session):
    return db.query(Eveniment).all()


def get_event_by_id(db: Session, event_id: int):
    return db.query(Eveniment).filter(Eveniment.ID == event_id).first()


def add_event(db: Session, ev: EventCreate, owner_id: int):
    db_event = Eveniment(
        ID_OWNER=owner_id,
        nume=ev.nume,
        locatie=ev.locatie,
        descriere=ev.descriere,
        numarLocuri=ev.numarLocuri
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, ev: dict):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return None


    if 'numarLocuri' in ev and ev['numarLocuri'] != db_event.numarLocuri:
        bilete_vandute = db.query(Bilet).filter(Bilet.EvenimentID == event_id).count()
        if bilete_vandute > 0:
            raise HTTPException(status_code=409,
                                detail="Numarul de locuri nu poate fi modificat deoarece exista bilete vandute.")

    for key, value in ev.items():
        if hasattr(db_event, key) and key != "ID":
            setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return False
    db.delete(db_event)
    db.commit()
    return True


# Functii Pachet

def list_pachete(db: Session):
    return db.query(Pachet).all()


def get_pachet_by_id(db: Session, pachet_id: int):
    return db.query(Pachet).filter(Pachet.ID == pachet_id).first()


def add_pachet(db: Session, p: PachetCreate, owner_id: int):
    db_pachet = Pachet(
        ID_OWNER=owner_id,
        nume=p.nume,
        locatie=p.locatie,
        descriere=p.descriere,
        numarLocuri=p.numarLocuri
    )
    db.add(db_pachet)
    db.commit()
    db.refresh(db_pachet)
    return db_pachet


def update_pachet(db: Session, pachet_id: int, p: dict):
    db_pachet = get_pachet_by_id(db, pachet_id)
    if not db_pachet:
        return None

    if 'numarLocuri' in p and p['numarLocuri'] != db_pachet.numarLocuri:
        bilete_vandute = db.query(Bilet).filter(Bilet.PachetID == pachet_id).count()
        if bilete_vandute > 0:
            raise HTTPException(status_code=409,
                                detail="Numarul de locuri nu poate fi modificat deoarece exista bilete vandute.")

    for key, value in p.items():
        if hasattr(db_pachet, key) and key != "ID":
            setattr(db_pachet, key, value)
    db.commit()
    db.refresh(db_pachet)
    return db_pachet


def delete_pachet(db: Session, pachet_id: int):
    db_pachet = get_pachet_by_id(db, pachet_id)
    if not db_pachet:
        return False
    # Stergere leg join_pe
    db_pachet.evenimente.clear()
    db.commit()
    db.delete(db_pachet)
    db.commit()
    return True


# Functii M-M

def list_events_in_pachet(db: Session, pachet_id: int):
    db_pachet = get_pachet_by_id(db, pachet_id)
    if not db_pachet:
        return None
    return db_pachet.evenimente


def add_event_to_pachet(db: Session, pachet_id: int, event_id: int):
    db_pachet = get_pachet_by_id(db, pachet_id)
    db_event = get_event_by_id(db, event_id)

    if not db_pachet or not db_event:
        raise HTTPException(status_code=404, detail="Pachetul sau evenimentul nu a fost gasit.")

    if db_event in db_pachet.evenimente:
        raise HTTPException(status_code=409, detail="Evenimentul este deja in pachet.")

    db_pachet.evenimente.append(db_event)
    db.commit()
    db.refresh(db_pachet)
    return db_pachet


# sterge leg M-M
def remove_event_from_pachet(db: Session, pachet_id: int, event_id: int):
    db_pachet = get_pachet_by_id(db, pachet_id)
    db_event = get_event_by_id(db, event_id)

    if not db_pachet or not db_event:
        raise HTTPException(status_code=404, detail="Pachetul sau evenimentul nu a fost gasit.")

    if db_event not in db_pachet.evenimente:
        raise HTTPException(status_code=404, detail="Legatura dintre pachet si eveniment nu exista.")

    db_pachet.evenimente.remove(db_event)
    db.commit()
    return True


# Functii bilete

def get_ticket_by_cod(db: Session, cod: str):
    return db.query(Bilet).filter(Bilet.COD == cod).first()


def list_event_tickets(db: Session, event_id: int):
    return db.query(Bilet).filter(Bilet.EvenimentID == event_id).all()


def list_pachet_tickets(db: Session, pachet_id: int):
    return db.query(Bilet).filter(Bilet.PachetID == pachet_id).all()


def create_event_ticket(db: Session, event_id: int):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evenimentul nu a fost gasit.")


    if db_event.numarLocuri is None:
        raise HTTPException(status_code=409,
                            detail="Nu se pot vinde bilete. Evenimentul nu are un numar de locuri setat.")

    bilete_vandute_count = db.query(Bilet).filter(Bilet.EvenimentID == event_id).count()
    if bilete_vandute_count >= db_event.numarLocuri:
        raise HTTPException(status_code=409, detail="Evenimentul este sold-out.")

    new_cod = str(uuid.uuid4())  # Genereaza cod unic
    db_bilet = Bilet(COD=new_cod, EvenimentID=event_id)
    db.add(db_bilet)
    db.commit()
    db.refresh(db_bilet)
    return db_bilet


def create_pachet_ticket(db: Session, pachet_id: int):
    db_pachet = get_pachet_by_id(db, pachet_id)
    if not db_pachet:
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit.")


    if db_pachet.numarLocuri is None:
        raise HTTPException(status_code=409, detail="Nu se pot vinde bilete. Pachetul nu are un numar de locuri setat.")


    bilete_pachet_vandute_count = db.query(Bilet).filter(Bilet.PachetID == pachet_id).count()
    if bilete_pachet_vandute_count >= db_pachet.numarLocuri:
        raise HTTPException(status_code=409, detail="Pachetul este sold-out.")


    # Verifica stocul individual al fiecarui eveniment din pachet
    for event in db_pachet.evenimente:
        if event.numarLocuri is not None:
            bilete_eveniment_vandute_count = db.query(Bilet).filter(Bilet.EvenimentID == event.ID).count()
            if bilete_eveniment_vandute_count >= event.numarLocuri:
                raise HTTPException(status_code=409,
                                    detail=f"Vanzarea a esuat. Evenimentul '{event.nume}' (parte a pachetului) este sold-out.")

    new_cod = str(uuid.uuid4())  # cod unic
    db_bilet = Bilet(COD=new_cod, PachetID=pachet_id)
    db.add(db_bilet)
    db.commit()
    db.refresh(db_bilet)
    return db_bilet


def delete_ticket(db: Session, cod: str):
    db_bilet = get_ticket_by_cod(db, cod)
    if not db_bilet:
        return False
    db.delete(db_bilet)
    db.commit()
    return True





