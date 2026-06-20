from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[schemas.EventOut])
def list_events(db: Session = Depends(get_db)):
    return crud.list_events(db)


@router.get("/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.post("/", response_model=schemas.EventOut)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db, event_in)


@router.put("/{event_id}", response_model=schemas.EventOut)
def update_event(event_id: int, event_in: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = crud.update_event(db, event_id, event_in)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    if not crud.delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return None


@router.post("/{event_id}/cancel", response_model=schemas.EventOut)
def cancel_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.cancel_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.post("/{event_id}/duplicate", response_model=schemas.EventOut)
def duplicate_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.duplicate_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.get("/{event_id}/history", response_model=List[schemas.EventHistoryOut])
def event_history(event_id: int, db: Session = Depends(get_db)):
    return crud.get_event_history(db, event_id)
