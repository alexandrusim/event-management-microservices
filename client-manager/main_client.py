import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from db_mongo import collection_clients
from models_client import ClientCreate, ClientInDB, TicketAdd
from dependencies import get_current_user

load_dotenv()

app = FastAPI(title="Client Manager API - MongoDB (Secured)")

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

EVENT_MANAGER_URL = os.getenv("EVENT_MANAGER_URL", "http://127.0.0.1:8000")


async def validate_ticket_exists(cod_bilet: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENT_MANAGER_URL}/api/event-manager/tickets/{cod_bilet}")

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Biletul nu exista in sistem.")

            response.raise_for_status()
            return response.json()

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Serviciul Event Manager nu raspunde.")


@app.get("/api/clients/me", response_model=ClientInDB, summary="Vezi profilul propriu")
def read_own_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    client_doc = collection_clients.find_one({"user_id": user_id})

    if not client_doc:
        raise HTTPException(status_code=404, detail="Nu aveti un profil de client creat.")

    return client_doc


@app.post("/api/clients", status_code=status.HTTP_201_CREATED, response_model=ClientInDB,
          summary="Creare profil propriu")
def create_client(
        client_data: ClientCreate,
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    if collection_clients.find_one({"user_id": user_id}):
        raise HTTPException(status_code=409, detail="Aveti deja un profil de client.")

    new_client = client_data.dict()
    new_client["user_id"] = user_id
    new_client["lista_bilete"] = []

    collection_clients.insert_one(new_client)

    return new_client


@app.post("/api/clients/me/tickets", summary="Adauga bilet la profilul propriu")
async def add_ticket_to_me(
        ticket: TicketAdd,
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    client_doc = collection_clients.find_one({"user_id": user_id})
    if not client_doc:
        raise HTTPException(status_code=404, detail="Creati-va intai profilul de client (POST /api/clients).")

    bilet_info = await validate_ticket_exists(ticket.cod)

    if ticket.cod in client_doc.get("lista_bilete", []):
        raise HTTPException(status_code=409, detail="Biletul este deja in portofelul dvs.")

    collection_clients.update_one(
        {"user_id": user_id},
        {"$push": {"lista_bilete": ticket.cod}}
    )

    return {"message": "Bilet adaugat cu succes", "ticket_info": bilet_info}


@app.get("/api/clients/me/tickets", summary="Vezi biletele mele")
async def get_my_tickets(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    client_doc = collection_clients.find_one({"user_id": user_id})
    if not client_doc:
        raise HTTPException(status_code=404, detail="Profil inexistent.")

    coduri_bilete = client_doc.get("lista_bilete", [])
    bilete_detaliate = []

    async with httpx.AsyncClient() as http_client:
        for cod in coduri_bilete:
            try:
                resp = await http_client.get(f"{EVENT_MANAGER_URL}/api/event-manager/tickets/{cod}")
                if resp.status_code == 200:
                    bilet_data = resp.json()
                    bilete_detaliate.append(bilet_data)
                else:
                    bilete_detaliate.append({"cod": cod, "status": "Invalid/Sters din EventManager"})
            except:
                bilete_detaliate.append({"cod": cod, "status": "Eroare conexiune"})

    return {"tickets": bilete_detaliate}

@app.get("/api/clients/ticket-owner/{cod_bilet}", summary="Gaseste proprietarul unui bilet")
def get_client_by_ticket(cod_bilet: str, current_user: dict = Depends(get_current_user)):

    client_doc = collection_clients.find_one({"lista_bilete": cod_bilet})

    if not client_doc:
        raise HTTPException(status_code=404, detail="Biletul nu este revendicat de niciun client.")

    return {
        "nume": client_doc.get("prenume_nume", "Anonim"),
        "email": client_doc.get("email"),
    }


@app.put("/api/clients/me", response_model=ClientInDB, summary="Actualizeaza profilul propriu")
def update_client_profile(
        client_update: ClientCreate,
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    client_doc = collection_clients.find_one({"user_id": user_id})
    if not client_doc:
        raise HTTPException(status_code=404, detail="Profilul nu exista.")

    update_data = client_update.dict(exclude_unset=True)

    if "user_id" in update_data: del update_data["user_id"]
    if "lista_bilete" in update_data: del update_data["lista_bilete"]

    collection_clients.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )

    updated_doc = collection_clients.find_one({"user_id": user_id})
    return updated_doc

