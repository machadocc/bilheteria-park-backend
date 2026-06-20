from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)


@router.get("/top-events", response_model=List[schemas.TopEventOut])
def top_events(db: Session = Depends(get_db)):
    return crud.get_top_events(db)


@router.get("/alerts", response_model=List[schemas.AlertOut])
def capacity_alerts(db: Session = Depends(get_db)):
    return crud.get_capacity_alerts(db)


@router.get("/last-sales", response_model=List[schemas.SaleOut])
def last_sales(db: Session = Depends(get_db)):
    return crud.get_last_sales(db)
