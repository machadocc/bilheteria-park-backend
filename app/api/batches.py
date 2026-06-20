from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/batches", tags=["Ticket Batches"])


@router.get("/", response_model=List[schemas.TicketBatchOut])
def list_batches(db: Session = Depends(get_db)):
    return crud.get_ticket_batches(db)


@router.post("/", response_model=schemas.TicketBatchOut)
def create_batch(batch_in: schemas.TicketBatchCreate, db: Session = Depends(get_db)):
    return crud.create_ticket_batch(db, batch_in)


@router.put("/{batch_id}", response_model=schemas.TicketBatchOut)
def update_batch(batch_id: int, batch_in: schemas.TicketBatchUpdate, db: Session = Depends(get_db)):
    batch = crud.update_ticket_batch(db, batch_id, batch_in)
    if not batch:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return batch


@router.post("/{batch_id}/close", response_model=schemas.TicketBatchOut)
def close_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = crud.close_ticket_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return batch
