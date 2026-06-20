from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=List[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.post("/", response_model=schemas.CustomerOut)
def create_customer(customer_in: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer_in)


@router.put("/{customer_id}", response_model=schemas.CustomerOut)
def update_customer(customer_id: int, customer_in: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    customer = crud.update_customer(db, customer_id, customer_in)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.get("/{customer_id}/history", response_model=List[schemas.SaleOut])
def customer_history(customer_id: int, db: Session = Depends(get_db)):
    if not crud.get_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return crud.get_customer_history(db, customer_id)
