import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import FastAPI, HTTPException, Query, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware

import grpc
import auth_pb2
import auth_pb2_grpc

from models import EventCreate, PachetCreate, Bilet, EventInPachet, Event, Pachet
from db.database import SessionLocal, Base, engine
from dependencies import get_current_user
import db.crud as crud
from db.models_db import Eveniment, Pachet as Pachet_DB, Bilet as Bilet_DB

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Manager API - MariaDB")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


CLIENT_MANAGER_URL = os.getenv("CLIENT_MANAGER_URL", "http://127.0.0.1:8001")
IDM_GRPC_ADDRESS = os.getenv("IDM_GRPC_ADDRESS", "localhost:50051")


class LoginRequestHTTP(BaseModel):
    email: str
    password: str


def make_event_repr(e: Eveniment):
    return {
        "event": {
            "id": e.ID, "id_owner": e.ID_OWNER, "nume": e.nume,
            "locatie": e.locatie, "descriere": e.descriere, "numarLocuri": e.numarLocuri
        },
        "_links": {
            "self": f"/api/event-manager/events/{e.ID}",
            "tickets": f"/api/event-manager/events/{e.ID}/tickets",
            "parent": "/api/event-manager/events",
            "clients": f"{CLIENT_MANAGER_URL}/api/clients"
        }
    }


def make_package_repr(p: Pachet_DB):
    return {
        "package": {
            "id": p.ID, "id_owner": p.ID_OWNER, "nume": p.nume,
            "locatie": p.locatie, "descriere": p.descriere, "numarLocuri": p.numarLocuri
        },
        "_links": {
            "self": f"/api/event-manager/event-packets/{p.ID}",
            "tickets": f"/api/event-manager/event-packets/{p.ID}/tickets",
            "events": f"/api/event-manager/event-packets/{p.ID}/events",
            "parent": "/api/event-manager/event-packets"
        }
    }


def make_ticket_repr(b: Bilet_DB):
    parent_url = "/api/event-manager/tickets"
    if b.PachetID:
        parent_url = f"/api/event-manager/event-packets/{b.PachetID}/tickets"
    elif b.EvenimentID:
        parent_url = f"/api/event-manager/events/{b.EvenimentID}/tickets"

    return {
        "ticket": {"cod": b.COD, "pachet_id": b.PachetID, "eveniment_id": b.EvenimentID},
        "_links": {"self": f"/api/event-manager/tickets/{b.COD}", "parent": parent_url}
    }


@app.exception_handler(OperationalError)
async def database_connection_exception_handler(request: Request, exc: OperationalError):
    print(f"Eroare conexiune DB: {exc}")
    return JSONResponse(
        status_code=502,
        content={"detail": "Serviciul de baza de date este momentan indisponibil (Database Down)."}
    )

@app.post("/api/auth/login", summary="Autentificare prin HTTP (Proxy catre gRPC)", tags=["Auth"])
def login_proxy(credentials: LoginRequestHTTP):
    try:
        with grpc.insecure_channel(IDM_GRPC_ADDRESS) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)

            response = stub.Login(auth_pb2.LoginRequest(
                username=credentials.email,
                password=credentials.password
            ))

            if response.token:
                return {"token": response.token}
            else:
                raise HTTPException(status_code=401, detail=response.error)

    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=f"Serviciul IDM indisponibil: {e}")


@app.get("/api/event-manager/events", summary="Listeaza toate evenimentele cu filtre si paginare")
def get_events(
        db: Session = Depends(get_db),
        name: Optional[str] = Query(None, description="Cautare cu potrivire partiala dupa nume"),
        location: Optional[str] = Query(None, description="Cautare dupa locatie exacta"),
        available_tickets: Optional[int] = Query(None, ge=1,
                                                 description="Filtreaza evenimente cu cel putin X bilete disponibile"),
        page: Optional[int] = Query(None, ge=1, description="Numarul paginii"),
        items_per_page: int = Query(10, ge=1, description="Elemente pe pagina")
):
    query = db.query(Eveniment)

    if name:
        query = query.filter(Eveniment.nume.ilike(f"%{name}%"))
    if location:
        query = query.filter(Eveniment.locatie == location)

    if available_tickets is not None:
        sold_sq = db.query(Bilet_DB.EvenimentID, func.count(Bilet_DB.COD).label("sold")) \
            .filter(Bilet_DB.EvenimentID != None) \
            .group_by(Bilet_DB.EvenimentID).subquery()

        query = query.outerjoin(sold_sq, Eveniment.ID == sold_sq.c.EvenimentID)
        query = query.filter(Eveniment.numarLocuri - func.coalesce(sold_sq.c.sold, 0) >= available_tickets)

    if page is not None:
        offset = (page - 1) * items_per_page
        query = query.offset(offset).limit(items_per_page)

    events = query.all()
    return {"events": [make_event_repr(e) for e in events]}


@app.get("/api/event-manager/events/{event_id}", summary="Obtine un eveniment dupa ID")
def get_event(event_id: int, db: Session = Depends(get_db)):
    e = crud.get_event_by_id(db, event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Evenimentul nu a fost gasit")
    return make_event_repr(e)


@app.post("/api/event-manager/events", status_code=201, summary="Creeaza un eveniment nou")
def create_event(
        ev: EventCreate,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["owner-event", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Nu aveti permisiunea de a crea evenimente."
        )

    existing = db.query(Eveniment).filter(Eveniment.nume == ev.nume).first()
    if existing:
        raise HTTPException(status_code=409, detail="Eveniment cu acest nume exista deja")

    new_event = crud.add_event(db, ev, owner_id=current_user["user_id"])
    return make_event_repr(new_event)


@app.put("/api/event-manager/events/{event_id}", summary="Actualizeaza un eveniment")
def replace_event(
        event_id: int,
        ev: EventCreate,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    event_db = crud.get_event_by_id(db, event_id)
    if not event_db:
        raise HTTPException(status_code=404, detail="Evenimentul nu a fost gasit")

    if event_db.ID_OWNER != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Nu puteti modifica evenimentele altui organizator.")

    updated = crud.update_event(db, event_id, ev.dict())
    return make_event_repr(updated)


@app.delete("/api/event-manager/events/{event_id}", summary="Sterge un eveniment")
def remove_event(
        event_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    event_db = crud.get_event_by_id(db, event_id)
    if not event_db:
        raise HTTPException(status_code=404, detail="Evenimentul nu a fost gasit")

    is_owner = (event_db.ID_OWNER == current_user["user_id"])
    is_admin = (current_user["role"] == "admin")

    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Nu puteti sterge evenimentele altui organizator.")

    crud.delete_event(db, event_id)
    return {"message": f"Evenimentul {event_id} a fost sters"}


@app.get("/api/event-manager/event-packets", summary="Listeaza toate pachetele de evenimente")
def get_packages(
        db: Session = Depends(get_db),
        name: Optional[str] = Query(None, description="Cautare cu potrivire partiala dupa nume"),
        location: Optional[str] = Query(None, description="Cautare dupa locatie exacta"),
        available_tickets: Optional[int] = Query(None, ge=1,
                                                 description="Filtreaza pachete cu cel putin X bilete disponibile"),
        page: Optional[int] = Query(None, ge=1, description="Numarul paginii"),
        items_per_page: Optional[int] = Query(10, ge=1, description="Elemente pe pagina")
):
    query = db.query(Pachet_DB)

    if name:
        query = query.filter(Pachet_DB.nume.ilike(f"%{name}%"))
    if location:
        query = query.filter(Pachet_DB.locatie == location)

    if available_tickets is not None:
        sold_sq = db.query(Bilet_DB.PachetID, func.count(Bilet_DB.COD).label("sold")) \
            .filter(Bilet_DB.PachetID != None) \
            .group_by(Bilet_DB.PachetID).subquery()

        query = query.outerjoin(sold_sq, Pachet_DB.ID == sold_sq.c.PachetID)
        query = query.filter(Pachet_DB.numarLocuri - func.coalesce(sold_sq.c.sold, 0) >= available_tickets)

    if page is not None:
        offset = (page - 1) * items_per_page
        query = query.offset(offset).limit(items_per_page)

    packages = query.all()
    return {"packages": [make_package_repr(p) for p in packages]}


@app.get("/api/event-manager/event-packets/{package_id}", summary="Obtine un pachet dupa ID")
def get_package(package_id: int, db: Session = Depends(get_db)):
    p = crud.get_pachet_by_id(db, package_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit")
    return make_package_repr(p)


@app.post("/api/event-manager/event-packets", status_code=201, summary="Creeaza un pachet nou")
def create_package(
        p: PachetCreate,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["owner-event", "admin"]:
        raise HTTPException(status_code=403, detail="Acces interzis.")

    existing = db.query(Pachet_DB).filter(Pachet_DB.nume == p.nume).first()
    if existing:
        raise HTTPException(status_code=409, detail="Pachet cu acest nume exista deja")

    new_package = crud.add_pachet(db, p, owner_id=current_user["user_id"])
    return make_package_repr(new_package)


@app.put("/api/event-manager/event-packets/{package_id}", summary="Actualizeaza un pachet")
def replace_package(
        package_id: int,
        p: PachetCreate,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    db_package = crud.get_pachet_by_id(db, package_id)
    if not db_package:
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit")

    if db_package.ID_OWNER != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Nu aveti permisiunea de a modifica acest pachet."
        )
    updated = crud.update_pachet(db, package_id, p.dict())
    return make_package_repr(updated)


@app.delete("/api/event-manager/event-packets/{package_id}", summary="Sterge un pachet")
def remove_package(
        package_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    db_package = crud.get_pachet_by_id(db, package_id)
    if not db_package:
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit")

    is_owner = (db_package.ID_OWNER == current_user["user_id"])
    is_admin = (current_user["role"] == "admin")

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=403,
            detail="Nu aveti permisiunea de a sterge acest pachet."
        )

    crud.delete_pachet(db, package_id)
    return {"message": f"Pachetul {package_id} a fost sters"}


@app.get("/api/event-manager/event-packets/{package_id}/events",
         response_model=List[Event],
         summary="Listeaza evenimentele dintr-un pachet")
def get_events_in_package(package_id: int, db: Session = Depends(get_db)):
    events = crud.list_events_in_pachet(db, package_id)
    if events is None:
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit")
    return events


@app.post("/api/event-manager/event-packets/{package_id}/events",
          summary="Adauga un eveniment intr-un pachet")
def add_event_to_package(package_id: int, item: EventInPachet, db: Session = Depends(get_db)):
    result = crud.add_event_to_pachet(db, package_id, item.event_id)
    return make_package_repr(result)


@app.delete("/api/event-manager/event-packets/{package_id}/events/{event_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Sterge un eveniment dintr-un pachet")
def remove_event_from_package(package_id: int, event_id: int, db: Session = Depends(get_db)):
    crud.remove_event_from_pachet(db, package_id, event_id)
    return None


@app.get("/api/event-manager/tickets/{cod}", summary="Obtine un bilet dupa cod")
def get_ticket(cod: str, db: Session = Depends(get_db)):
    b = crud.get_ticket_by_cod(db, cod)
    if not b:
        raise HTTPException(status_code=404, detail="Biletul nu a fost gasit")
    return make_ticket_repr(b)


@app.delete("/api/event-manager/tickets/{cod}", summary="Invalideaza/Sterge un bilet")
def invalidate_ticket(
        cod: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    db_ticket = crud.get_ticket_by_cod(db, cod)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Biletul nu a fost gasit")

    user_id = current_user["user_id"]
    user_role = current_user["role"]

    if user_role == 'admin':
        crud.delete_ticket(db, cod)
        return {"message": f"Biletul {cod} a fost sters (ADMIN override)."}

    if user_role == 'owner-event':
        has_permission = False

        if db_ticket.EvenimentID:
            event = crud.get_event_by_id(db, db_ticket.EvenimentID)
            if event and event.ID_OWNER == user_id:
                has_permission = True

        elif db_ticket.PachetID:
            pachet = crud.get_pachet_by_id(db, db_ticket.PachetID)
            if pachet and pachet.ID_OWNER == user_id:
                has_permission = True

        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail="Nu aveti permisiunea de a sterge acest bilet (nu va apartine evenimentul/pachetul)."
            )

        crud.delete_ticket(db, cod)
        return {"message": f"Biletul {cod} a fost invalidat/sters"}

    raise HTTPException(status_code=403, detail="Nu aveti dreptul de a sterge bilete.")


@app.get("/api/event-manager/events/{event_id}/tickets", summary="Listeaza biletele unui eveniment")
def get_event_tickets(event_id: int, db: Session = Depends(get_db)):
    if not crud.get_event_by_id(db, event_id):
        raise HTTPException(status_code=404, detail="Evenimentul nu a fost gasit")
    tickets = crud.list_event_tickets(db, event_id)
    return {"tickets": [make_ticket_repr(t) for t in tickets]}


@app.post("/api/event-manager/events/{event_id}/tickets",
          status_code=201,
          summary="Vinde (creeaza) un bilet nou pentru eveniment")
def sell_event_ticket(event_id: int, db: Session = Depends(get_db)):
    try:
        new_ticket = crud.create_event_ticket(db, event_id)
        return make_ticket_repr(new_ticket)
    except HTTPException as e:
        raise e


@app.get("/api/event-manager/event-packets/{package_id}/tickets", summary="Listeaza biletele unui pachet")
def get_package_tickets(package_id: int, db: Session = Depends(get_db)):
    if not crud.get_pachet_by_id(db, package_id):
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit")
    tickets = crud.list_pachet_tickets(db, package_id)
    return {"tickets": [make_ticket_repr(t) for t in tickets]}


@app.post("/api/event-manager/event-packets/{package_id}/tickets",
          status_code=201,
          summary="Vinde (creeaza) un bilet nou pentru pachet")
def sell_package_ticket(package_id: int, db: Session = Depends(get_db)):
    try:
        new_ticket = crud.create_pachet_ticket(db, package_id)
        return make_ticket_repr(new_ticket)
    except HTTPException as e:
        raise e