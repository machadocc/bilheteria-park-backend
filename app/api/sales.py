from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/checkout", response_model=schemas.SaleOut)
def checkout_sale(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    try:
        sale = crud.create_sale(db, sale_in)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return sale


@router.get("/catalog", response_model=List[schemas.EventOut])
def event_catalog(db: Session = Depends(get_db)):
    return crud.list_events(db)
