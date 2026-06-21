from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(tags=["Purchases"])


@router.post("/compras", response_model=schemas.SaleOut)
def purchase_ticket(purchase_in: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    try:
        sale = crud.create_purchase(db, purchase_in)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return sale
